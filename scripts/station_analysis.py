#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 10:01:20 2021

@author: lukem
"""

import pandas as pd
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as feat
import matplotlib.path as mpath
import matplotlib.cm as cm
import psycopg2
import getpass
import os
from datetime import date
import sys

def stationsCSV(definedStationsFilepath, data):
    '''
    Load dataframe of all stations with their coordinates
    In this case, this should be the intended coordinate if available, not the coordinate visisted
    If this is not available, will use mean of all coordinates visited for that station
    
    Parameters
    ----------
    definedStationsFilepath : string
        Filepath for csv file that contains the names and locations of officially defined stations for the project
    data: pandas.dataframe
        Dataframe of all samples in database
    
    Returns
    -------
    stations : pandas.dataframe
        Dataframe of all stations and their defined or average coordinates
    '''
    stations = pd.read_csv(definedStationsFilepath) # Defined stations
    
    del stations['eventID'], stations['sampleType'] # Removing columns not needed
    
    otherStations = set(data['stationname'])  
    
    n = 0
    for station in otherStations:
        if station not in list(stations['stationName']) and type(station) == str: # Stations not already defined
            # Calculating average coordinates for each station
            n += 1
            samplesdf = data.loc[data['stationname'] == station]
            lat = samplesdf['decimallatitude'].median()
            lon = samplesdf['decimallongitude'].median()
            newRow = {'stationName': station, 'decimalLongitude': lon, 'decimalLatitude': lat}
            stations = stations.append(newRow, ignore_index=True)
        else:
            pass

    return stations

def distanceCoordinates(lat1,lon1,lat2, lon2):
    '''
    Calculates the distance between two decimal coordinates on earth based on the haversine equation for spherical trigonometry

    Parameters
    ----------
    lat1 : float
        Decimal latitude of 1st point
    lat2 : float
        Decimal latitude of 2nd point.
    lon1 : float
        Decimal longitude of 1st point
    lon2 : float
        Decimal longitude of 2nd point

    Returns
    -------
    Distance in kilometres

    '''
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)
    
    # approximate radius of earth in km
    R = 6373.0
    
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    distance = R * c # distance in kilometres
    
    return distance

def closeStations(stations, op_filepath):
    '''
    Function that creates a CSV that includes stations that are close to one another
    
    Parameters
        ----------
        stations : pandas.dataframe
            Dataframe of all stations and their defined or average coordinates
        
        op_filepath : string
            Where to write the CSV file to
    '''

    stations = stations.sort_values(by=['stationName'])
    closeStations = pd.DataFrame(columns=['Station 1', 'Station 2', 'Distance between stations (km)'])
    for idx, row in stations.iterrows():
        name1 = row['stationName']
        distances = list(stations.apply(lambda s : distanceCoordinates(s['decimalLatitude'], s['decimalLongitude'], row['decimalLatitude'], row['decimalLongitude']), axis=1))
        for i, distance in enumerate(distances):
            name2 = stations['stationName'].iloc[i]
            if 0 < distance < 5: # Maximum distance between stations for them to be considered close together and include in CSV
                newRow = {'Station 1': name1, 'Station 2': name2, 'Distance between stations (km)': distance}
                closeStations = closeStations.append(newRow, ignore_index=True)
    closeStations.to_csv(op_filepath)
    
def plotMap(op_filepath, latMinPlot, lonMinPlot, latMaxPlot, lonMaxPlot, samples=None, stations=None, title=None):
    '''
    Plots a map that can be used to show where samples were taken and/or stations

    Parameters
    ----------
    op_filepath : string
        The filepath where the map will be stored.
    latMinPlot : int
        Minimum latitude to plot, decimal coordinates
    lonMinPlot : int
        Minimum longitude to plot, decimal coordinates
    latMaxPlot : int
        Maximum latitude to plot, decimal coordinates
    lonMaxPlot : int
        Maximum longitude to plot, decimal coordinates
    samples : pandas.dataframe, optional
        Samples to plot on map. The default is None.
    stations : pandas.dataframe, optional
        Stations to plot on map. The default is None.
    title : string, optional
        Option to include a title above the map. The default is None.

    Returns
    -------
    None.

    '''
    plt.figure(figsize = (7,7))
    ax = plt.axes(projection=ccrs.EquidistantConic())
    ax.gridlines(draw_labels=True, linewidth=1, color='k', linestyle='--')
    ax.add_feature(feat.NaturalEarthFeature('physical', 'land', '10m',
                                            facecolor=feat.COLORS['land'],
                                            edgecolor='black',
                                            linewidth=1.2))
    xlim = [lonMinPlot, lonMaxPlot]
    ylim = [latMinPlot, latMaxPlot]
    
    rect = mpath.Path([[xlim[0], ylim[0]],
                       [xlim[1], ylim[0]],
                       [xlim[1], ylim[1]],
                       [xlim[0], ylim[1]],
                       [xlim[0], ylim[0]],
                       ]).interpolated(20)
    
    proj_to_data = ccrs.PlateCarree()._as_mpl_transform(ax) - ax.transData
    rect_in_target = proj_to_data.transform_path(rect)
    
    ax.set_boundary(rect_in_target)
    
    # Notice the ugly hack to stop any further clipping - this is
    # the same problem as #363.
    ax.set_extent([xlim[0], xlim[1], ylim[0] - 2, ylim[1]])
    ax.stock_img()
    
    if samples is not None:
        cruises = list(set(samples['cruisenumber'].astype(str)))
        colors = cm.rainbow(np.linspace(0, 1, len(cruises)))
        for cruise, color in zip(cruises, colors):
            cruiseSamples = samples.loc[samples['cruisenumber'].astype(str) == cruise]
            ax.scatter(cruiseSamples['decimallongitude'],cruiseSamples['decimallatitude'],color=color,edgecolor='k',marker='.',s=200,transform=ccrs.PlateCarree(), zorder=5, label=cruise)
    if stations is not None:
        ax.scatter(stations['decimalLongitude'],stations['decimalLatitude'],color='grey',edgecolor='k',marker='s',s=200,transform=ccrs.PlateCarree(), zorder=3, label='Stations')
    if title is not None:
        ax.set_title(title, fontsize=18)
    
    plt.legend(bbox_to_anchor = (1.1, 1.1))
    plt.savefig(op_filepath, bbox_inches='tight')
    plt.close()
    
    
class Station:
    
    def __init__(self,name,latitude,longitude):
        self.name = name
        self.name = self.name.replace('/','_')
        print(self.name)
        self.latitude = latitude
        self.longitude = longitude

    def findSamples(self, data):
        '''
        Create a dataframe that includes samples just from an individual station

        Parameters
        ----------
        data : pandas.dataframe
            Dataframe of all samples in database

        Returns
        -------
        samplesdf : pandas.dataframe
            Dataframe of samples from single station

        '''
        self.samples = data.loc[data['stationname'] == self.name]
    
    def plotDistanceSamplesStation(self, op_filepath):
        '''
        Function that plots how close samples from a particular station are from the station coordinates
        The station coordinates are either manually predefined, or taken as the average of the sample coordinates
        '''

        samples = self.samples.copy()
        print(samples)
        samples['distance from station'] = samples.apply(lambda row : distanceCoordinates(self.latitude, self.longitude, row['decimallatitude'], row['decimallongitude']), axis = 1)
        
        if len(self.samples) > 5: # Only consider stations less than 10 km from each other
            numActivities = len(samples)
            samples = samples.sort_values(by='distance from station')
            samples = samples.reset_index(drop=True)
            samples['percent activities'] = 100 * (samples.index + 1) / numActivities
            fig, ax = plt.subplots()
            cruises = list(set(samples['cruisenumber'].astype(str)))
            colors = cm.rainbow(np.linspace(0, 1, len(cruises)))
            for cruise, color in zip(cruises, colors):
                cruiseSamples = samples.loc[samples['cruisenumber'].astype(str) == cruise]
                ax.scatter(cruiseSamples['distance from station'], cruiseSamples['percent activities'], color=color, label=cruise)
            ax.set_xlabel('Distance from station coordinates (km)')
            ax.set_ylabel('% of activities within this distance')
            xmin, xmax = ax.get_xlim()
            ax.set_xlim(0,xmax)
            ax.set_ylim([0,100])
            ax.set_title(f'{self.name}: {self.latitude:.4f}$^\circ$N {self.longitude:.4f}$^\circ$E')
            plt.legend()
            plt.savefig(op_filepath+self.name)
            plt.close()
    
    def mapSamplesOneStation(self, op_filepath):
        '''
        Setup for plotting map for a single station.

        Parameters
        ----------
        op_filepath : string
            The directory where the map will be stored. Filename will be appended to this, from station name.

        Returns
        -------
        None.

        '''
        if len(self.samples) > 0 and self.name not in ['ADCPstart_75kHz','ADCPstart_38kHz','ISF']:
        #if self.name == 'M5':
            
            
            # if self.name == 'G8/H1':
            #     op_filepath = op_filepath + 'G8H1'
            # else:
            #     op_filepath = op_filepath + self.name
            
            # Maximum and minimum of lat/lon for samples logged as being from this station
            latMin = self.samples['decimallatitude'].min()
            latMax = self.samples['decimallatitude'].max()
            lonMin = self.samples['decimallongitude'].min()
            lonMax = self.samples['decimallongitude'].max()
            
            # Defining minimum area to plot, that encapsulates Svalbard and the NE Barents Sea
            latMinPlot = 76 if latMin - 1 > 76 else latMin - 1
            lonMinPlot = 11 if lonMin - 3 > 11 else lonMin - 3
            latMaxPlot = 81 if latMax + 1 < 81 else latMax + 1
            lonMaxPlot = 28 if lonMax + 3 < 28 else lonMax + 3
            
            samples = self.samples
            dic = {
                'stationName': [self.name],
                'decimalLatitude': [self.latitude],
                'decimalLongitude': [self.longitude]
                }
            
            stations = pd.DataFrame(dic, columns=['stationName','decimalLatitude', 'decimalLongitude'])
            stations = None
            title = self.name
            
            plotMap(op_filepath, latMinPlot, lonMinPlot, latMaxPlot, lonMaxPlot, samples=samples, stations=stations, title=title)
            
def main():

    conn = psycopg2.connect('dbname=aen_db user=' + getpass.getuser())
    data = pd.read_sql_query("SELECT * FROM aen",con=conn)
    '''
    Discarding samples with a parent event ID,
    thus keeping only activities at top of pyramid
    This is so only a single sample is kept for each activity. All children should have same coordinates as their parent.
    '''
    data = data[data['parenteventid'].isna()]
    
    today = date.today().strftime("%Y_%m_%d")
    folder = 'station_analysis_' + today
    try: 
        os.mkdir(folder)
    except OSError as error: 
        print(error)
    
    try: 
        os.mkdir(folder+'/distance_from_station/')
    except OSError as error: 
        print(error)
        
    try: 
        os.mkdir(folder+'/map_samples_from_station/')
    except OSError as error: 
        print(error)
        
    stations = stationsCSV('stations.csv', data)
    
    closeStations(stations,folder+'/closeStations.csv')
    
    for idx,row in stations.iterrows():
        name = row['stationName']
        lat = row['decimalLatitude']
        lon = row['decimalLongitude']
        station = Station(name, lat, lon)
        station.findSamples(data)
        if len(station.samples) > 0:
            station.plotDistanceSamplesStation(folder+'/distance_from_station/')
            station.mapSamplesOneStation(folder+'/map_samples_from_station/')
    
    print('Files written to ' + folder)
        
if __name__ == "__main__":
    sys.exit(main())

#%%

P7 (NLEG25_NPAL16)_box core