import os
from datetime import datetime
from pathlib import Path

import pandas as pd

import networkx as nx
import osmnx as ox

import matplotlib.pyplot as plt
import imageio as iio


def get_shortest_paths(G, origin_nodes: list, destination_nodes: list, weight: str):
    """
    This function calculates the shortest paths based on weight parameter.
    ---
    Args:
        origin_nodes (list): list of origin nodes
        destination_nodes (list): list of destination nodes
        weight (str): graph property for shortest path calculation
    """
    route_list = []
    nan_index_list = []

    for index, node in enumerate(origin_nodes):
        origin = origin_nodes[index]
        destination = destination_nodes[index]
        route = ox.shortest_path(G, origin, destination, weight=weight)

        if route and isinstance(route, list):
            route_list.append(route)
        else:
            nan_index_list.append(index)

    print(f'Generated {len(route_list)} routes from {len(origin_nodes)} origins and {len(destination_nodes)} destinations.')
    print(f'{len(nan_index_list)} routes returned NaN.')

    return route_list, nan_index_list


def create_g(df):
    """
    """
    centroid = [60.1699, 24.9384]
    mode = "drive"
    G = ox.graph_from_point(centroid, dist=2000, simplify=True, network_type=mode)

    origin_nodes = ox.distance.nearest_nodes(G, X=df['VENUE_LONG'], Y=df['VENUE_LAT'])
    destination_nodes = ox.distance.nearest_nodes(G, X=df['USER_LONG'], Y=df['USER_LAT'])

    return G, origin_nodes, destination_nodes


def plot_routes(G: nx.Graph, df: pd.DataFrame, route_list: list, start, end, hour, day):
    """
    This function Plots routes within a specified date range.
    ---
    Args:
        G (nx.Graph): network x Graphs
        df (pd.DataFrame):
        routes (list): routes as a list
        start (datetime): index for filtering the routes
        end (datetime): index for filtering the routes

    Returns: None
    """

    window = df[(df['TIMESTAMP'] >= start) & (df['TIMESTAMP'] <= end)]
    routes_to_plot = route_list[0: len(window)]

    fig, ax = ox.plot_graph_routes(G,
                                   routes_to_plot,
                                   route_colors='#3cb4dc',
                                   route_linewidth=3,
                                   route_alpha=0.9,
                                   save=True,
                                   filepath=f'images/day_{day}_hour_{hour}.png',
                                   node_size=7)


def generate_images(G, df, route_list):
    """
    """
    year = 2020
    month = 9
    day_range = range(1, 14)
    hour_range = range(7, 19)

    for day in day_range:
        for hour in hour_range:
            next_hour = hour + 1
            start = datetime(year, month, day, hour)
            end = datetime(year, month, day, next_hour)

            plot_routes(G, df, route_list, start, end, hour, day)


def main_images(path, filenames):
    images = list()
    for file in Path(path).iterdir():
        im = iio.imread(file)
        images.append(im)

    duration = 0.25
    iio.mimsave(f'wolt_{duration}.gif', images, duration=duration)


def main():
    path = '../images/'
    filenames = os.listdir(path)

    if len(filenames) == 0:
        df = pd.read_csv('data/orders.csv')
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
        print(df.head())

        G, origin_nodes, destination_nodes = create_g(df)

        weight = 'travel_time'
        route_list, nan_index = get_shortest_paths(G, origin_nodes, destination_nodes, weight)
        df = df.drop(df.index[nan_index])
        print(route_list)

        generate_images(G, df, route_list)

    main_images(path, filenames)
    print('done')


if __name__ == '__main__':
    main()
