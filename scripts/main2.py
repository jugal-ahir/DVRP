import argparse
from random import seed
from simulation import Simulation
from config import *
import pygame
import imageio
import numpy as np
from importlib import import_module
from os import path, mkdir
from time import time, sleep
from pickle import load, dump
from math import floor
import osmnx as ox  # NEW: Import OpenStreetMap (OSM) for real-world maps
import networkx as nx  # NEW: Import networkx for shortest path routing

def load_real_world_map(location="Manhattan, New York, USA"):
    """NEW FUNCTION: Load a real-world road network from OpenStreetMap."""
    print(f"Loading real-world road network for {location}...")
    G = ox.graph_from_place(location, network_type='drive')  # Load drivable roads
    return G

def get_shortest_path(G, source, target):
    """NEW FUNCTION: Compute the shortest path between two points using real road network."""
    source_node = ox.distance.nearest_nodes(G, source[0], source[1])
    target_node = ox.distance.nearest_nodes(G, target[0], target[1])
    path = nx.shortest_path(G, source=source_node, target=target_node, weight='length')
    return path

def simulate(args, delivery_log=None):
    if args.show_sim:
        pygame.init()
        size = (args.width, args.height)
        screen = pygame.display.set_mode(size)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.display.set_caption('ITS 4 PROJECT : CSE 400')
        clock = pygame.time.Clock()
        pygame.font.init()
    elif args.record_data:
        size = (args.width, args.height)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.font.init()
    else:
        screen = None

    if args.seed is not None:
        seed(args.seed)
        print("Setting seed to: ", args.seed)
    else:
        seed(time())

    if args.total_tasks < args.max_tasks:
        args.total_tasks = args.max_tasks

    if args.initial_tasks < 0:
        if args.service_time:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd*args.service_time)**2))
        else:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd)**2))

    generator_args = GENERATOR_ARGS
    generator_args.update({
        'seed': args.seed,
        'max_time': args.max_time,
        'service_time': args.service_time,
        'initial_tasks': args.initial_tasks,
        'max_initial_wait': args.max_initial_wait,
        'total_tasks': args.total_tasks,
        'data_source': args.data_source,
        'sectors': args.sectors,
        'centralized': args.centralized
    })

    # NEW: Load real-world map
    real_map = load_real_world_map("San Francisco, California, USA")
    print("Real-world map loaded successfully!")

    sim = Simulation(
        policy_name=args.policy,
        generator_name=args.generator,
        policy_args={
            'cost_exponent': args.cost_exponent,
            'eta': args.eta,
            'eta_first': args.eta_first,
            'gamma': args.gamma,
            'sectors': args.sectors,
        },
        generator_args=generator_args,
        num_actors=args.actors,
        pois_lambda=args.lambd,
        service_time=args.service_time,
        screen=surface if args.show_sim or args.record_data else None,
        max_tasks=args.max_tasks,
        max_time=args.max_time,
        record_data=args.record_data,
        centralized=args.centralized,
        delivery_log=delivery_log
    )

    frames = []
    gif_filename = f"simulation_{('Hello')}.gif" if args.record_gif else None

    while True:
        if args.show_sim:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if args.record_gif and frames:
                        print(f"Saving GIF as {gif_filename}...")
                        imageio.mimsave(gif_filename, frames, fps=30)
                    return

        rval = sim.tick(tick_time=args.tick_time, max_simulation_time=args.max_time, max_tasks=args.max_tasks)
        if rval == -1:
            if args.record_gif and frames:
                print(f"Saving GIF as {gif_filename}...")
                imageio.mimsave(gif_filename, frames, fps=30)
            break

        if args.show_sim:
            screen.blit(surface, (0, 0))
            pygame.display.flip()

            if args.record_gif:
                data = pygame.surfarray.array3d(screen)
                data = np.flipud(np.rot90(data))
                frames.append(data)
            
            clock.tick(1.0/args.tick_time*args.simulation_speed)

    if len(sim.serviced_tasks) > 0:
        print("Average service time:", sim._avg_served_time / len(sim.serviced_tasks))
    print("Total serviced:", len(sim.serviced_tasks))
    return sim

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument('--record-gif', action='store_true', help='Record the simulation as a GIF file')
    argparser.add_argument('--show-sim', action='store_true', help='Display the simulation window')
    argparser.add_argument('--height', default=SCREEN_HEIGHT, type=int, help='Screen vertical size')
    argparser.add_argument('--width', default=SCREEN_WIDTH, type=int, help='Screen horizontal size')
    argparser.add_argument('-s', '--seed', default=None, type=int, help='Random Seed')
    argparser.add_argument('-l', '--lambd', default=LAMBDA, type=float, help='Exponential Spawn rate for Tasks')
    argparser.add_argument('--eta', default=DEFAULT_POLICY_ETA, type=float, help='Proportion of policy to execute (batch) (0,1]')
    argparser.add_argument('-a', '--actors', default=NUM_ACTORS, type=int, help='Number of actors in the simulation')
    argparser.add_argument('-p', '--policy', default=DEFAULT_POLICY_NAME, help='Policy to use')
    argparser.add_argument('-g', '--generator', default=DEFAULT_GENERATOR_NAME, help='Random Generator to use')
    argparser.add_argument('--simulation-speed', default=SIMULATION_SPEED, type=float, help='Simulator speed')
    argparser.add_argument('-t', '--tick-time', default=TICK_TIME, type=float, help='Length of Simulation Time Step')
    argparser.add_argument('--max-time', default=None, type=float, help='Maximum Length of Simulation')
    args = argparser.parse_args()

    simulate(args)
