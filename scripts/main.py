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
        # pygame.init()
        size = (args.width, args.height)
        surface = pygame.Surface(size, pygame.SRCALPHA)
        pygame.font.init()
    else:
        screen = None

    # for i in range(15):
    #     sleep(1)

    # set the seed
    if args.seed is not None:
        seed(args.seed)
        print("Setting seed to: ", args.seed)
    else:
        seed(time())

    if args.total_tasks < args.max_tasks:
        args.total_tasks = args.max_tasks

    # override initial tasks
    if args.initial_tasks < 0:
        if args.service_time:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd*args.service_time)**2))
        else:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd)**2))

    generator_args = GENERATOR_ARGS
    generator_args['seed'] = args.seed
    generator_args['max_time'] = args.max_time
    generator_args['service_time'] = args.service_time
    generator_args['initial_tasks'] = args.initial_tasks
    generator_args['max_initial_wait'] = args.max_initial_wait
    generator_args['total_tasks'] = args.total_tasks
    generator_args['data_source'] = args.data_source
    generator_args['sectors'] = args.sectors
    generator_args['centralized'] = args.centralized

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

    if args.seed is not None and args.data_source is None:
        # if not path.isdir(TASKS_DIR):
        #     mkdir(TASKS_DIR)

        # tasks_str = '_' + str(args.initial_tasks) + 'i' + '_' + str(args.total_tasks) + 'tt'

        # # TODO: so far everything has run with 1000 tasks -- should codify that in the file name
        # pickle_file = path.join(TASKS_DIR, TASK_LIST_FILE_PREFIX + tasks_str + '_' + str(args.lambd) +
        #                         '_' + str(args.generator) + '_' + str(args.seed) + '.pkl')
        # try:
        #     with open(pickle_file, 'rb') as fp:
        #         task_list = load(fp)
        #         sim.reset(task_list)
        # except Exception as e:
        #     print(e)
        #     # not loading, save it instead
        #     with open(pickle_file, 'wb') as fp:
        #         dump(sim.task_list, fp)
        pass
    frames = []
    if args.record_gif:  # Add this as a command line argument
        gif_filename = f"simulation_{('Hello')}.gif"

    while True:
        if args.show_sim:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # Save GIF when window is closed
                    if args.record_gif and frames:
                        print(f"Saving GIF as {gif_filename}...")
                        imageio.mimsave(gif_filename, frames, fps=30)
                    return

        rval = sim.tick(tick_time=args.tick_time, max_simulation_time=args.max_time, max_tasks=args.max_tasks)
        if rval == -1:
            # Save GIF when simulation completes
            if args.record_gif and frames:
                print(f"Saving GIF as {gif_filename}...")
                imageio.mimsave(gif_filename, frames, fps=30)
            break

        if args.show_sim:
            screen.blit(surface, (0, 0))
            pygame.display.flip()
            
            # Capture frames if recording
            if args.record_gif:
                data = pygame.surfarray.array3d(screen)
                data = np.flipud(np.rot90(data))
                frames.append(data)
            
            clock.tick(1.0/args.tick_time*args.simulation_speed)


    if len(sim.serviced_tasks) > 0:
        print("Average service time:", sim._avg_served_time/len(sim.serviced_tasks))
    print("Total serviced:", len(sim.serviced_tasks))
    return sim


def multiple_sims(args):

    if not path.isdir(RESULTS_DIR):
        mkdir(RESULTS_DIR)

    # Note that neither batch_tsp, nor tsp use the exponent value for anything -- they
    # just need to run once... giving them unique negative values in case we want to graph
    # them

    if len(args.prefix) != 0 and args.prefix[-1] != '_':
        args.prefix = args.prefix + '_'

    if args.seed is None:
        seeds = [21, 6983, 42, 520, 97, 29348, 935567]
        seed_str = ''
    else:
        seeds = [args.seed, ]
        seed_str = '_' + str(args.seed) + 's'

    if args.eta_first:
        eta_str = str(args.eta) + 'ef_'
    else:
        eta_str = str(args.eta) + 'e_'

    results_str = args.prefix + args.policy + '_' + str(args.sectors) + 'sc_' + str(args.cost_exponent) + 'p_' + eta_str + \
        str(args.lambd) + 'l_' + str(args.service_time) + 't' + seed_str + ".csv"
    results_file_name = path.join(RESULTS_DIR, results_str)
    f = open(results_file_name, 'w')
    f.write('policy,seed,lambda,rho,sectors,cost-exponent,eta,eta-first,sim-time,avg-srv-time,tasks-srvd,max-wait-time,avg-wait-time,wait-sd,total-travel-distance,avg-agent-dist,avg-task-dist,max-agent-dist,max_queue_len\n')
    f.flush

    delivery_log_str = 'DeliveryLog_' + results_str
    delivery_log_name = path.join(RESULTS_DIR, delivery_log_str)
    delivery_log = open(delivery_log_name, 'w')
    delivery_log.write('id,px,py,t_arrive,t_service,t_initial\n')
    delivery_log.flush()

    if args.initial_tasks < 0:
        # estimate the pending queue based on lambda
        if args.service_time:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd*args.service_time)**2))
        else:
            args.initial_tasks = floor(args.lambd * BETA**2 / ((1-args.lambd)**2))

    for seed in seeds:
        args.seed = seed
        print(f"================= LAMBDA: {args.lambd}, SEED: {seed} =================")
        sim = simulate(args, delivery_log)
        policy = args.policy.replace('_', ' ')
        f.write(
            str(policy) + "," + str(args.seed) + "," + str(args.lambd) + "," + str(sim.rho) + "," + str(args.sectors) + "," + str(args.cost_exponent) + "," + str(args.eta) + "," + str(args.eta_first) + "," + str(sim.sim_time) + "," + str(sim._avg_served_time) + "," + str(len(sim.serviced_tasks)) + "," +
            str(sim._max_served_time) + "," + str(sim._avg_served_time / len(sim.serviced_tasks)) + "," + str(sim.calculate_sd()) + "," +
            str(sim._total_travel_distance) + "," +
            str(sim._total_travel_distance / len(sim.actor_list)) + "," + str(sim._total_travel_distance / len(sim.serviced_tasks)) + "," +
            str(sim._max_travel_distance) + "," + str(sim._max_queue_length) + "\n"
        )
        f.flush()

        if args.actor_stats:
            actor_stats_file = path.join(RESULTS_DIR, args.prefix + 'actor_' + args.policy + '_' +
                                         str(args.cost_exponent) + '_' + str(args.service_time) + ".csv")
            if not path.exists(actor_stats_file):
                with open(actor_stats_file, 'w') as fp:
                    fp.write('cost-exponent,actor,time,changes,max-changes,path-len\n')

            with open(actor_stats_file, 'a') as fp:
                for actor in range(len(sim.actor_list)):
                    for (time, changes, max_changes, length) in sim.actor_list[actor].history:
                        fp.write(str(args.cost_exponent) + ',' + str(actor) + ',' + str(time) + ',' +
                                 str(changes) + ',' + str(max_changes) + ',' + str(length) + "\n")
                fp.flush()

    delivery_log.close()
    f.close()


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description=__doc__)
    argparser.add_argument(
        '--actor-stats',
        action='store_true',
        help="Record the actor's queue history for the entire test")
    argparser.add_argument(
    '--record-gif',
    action='store_true',
    help='Record the simulation as a GIF file')
    argparser.add_argument(
        '--height',
        default=SCREEN_HEIGHT,
        type=int,
        help='Screen vertical size')
    argparser.add_argument(
        '--width',
        default=SCREEN_WIDTH,
        type=int,
        help='Screen horizontal size')
    argparser.add_argument(
        '--margin',
        default=SCREEN_MARGIN,
        type=int,
        help='Screen horizontal size')
    argparser.add_argument(
        '-s', '--seed',
        default=None,
        type=int,
        help='Random Seed')
    argparser.add_argument(
        '-l', '--lambd',
        default=LAMBDA,
        type=float,
        help='Exponential Spawn rate for Tasks')
    argparser.add_argument(
        '--eta',
        default=DEFAULT_POLICY_ETA,
        type=float,
        help='Proportion of policy to execute (batch) (0,1]')
    argparser.add_argument(
        '--gamma',
        default=DEFAULT_POLICY_GAMMA,
        type=float,
        help='Insertion threshold [0,1)')
    argparser.add_argument(
        '-c', '--cost-exponent',
        default=DEFAULT_POLICY_COST_EXPONENT,
        type=float,
        help='Power of Cost Function for Min Wait')
    argparser.add_argument(
        '-a', '--actors',
        default=NUM_ACTORS,
        type=int,
        help='Number of actors in the simulation')
    argparser.add_argument(
        '-p', '--policy',
        default=DEFAULT_POLICY_NAME,
        help='Policy to use')
    argparser.add_argument(
        '--prefix',
        default="",
        help='Prefix on results file name')
    argparser.add_argument(
        '-g', '--generator',
        default=DEFAULT_GENERATOR_NAME,
        help='Random Generator to use')
    argparser.add_argument(
        '--initial-tasks',
        default=0,
        type=int,
        help='Pending tasks at the start of the simulation (t=0).  If -1, waiting tasks will be scaled relative to lambda.')
    argparser.add_argument(
        '--max-initial-wait',
        default=0,
        type=float,
        help='Initial tasks will have a waiting time randomly drawn from [0,max).')
    argparser.add_argument(
        '--load-tasks',
        action='store_true',
        help='Load the most recent list of tasks')
    argparser.add_argument(
        '--service-time',
        default=SERVICE_TIME,
        type=float,
        help='Service time on arrival at each node')
    argparser.add_argument(
        '--simulation-speed',
        default=SIMULATION_SPEED,
        type=float,
        help='Simulator speed')
    argparser.add_argument(
        '-t', '--tick-time',
        default=TICK_TIME,
        type=float,
        help='Length of Simulation Time Step')
    argparser.add_argument(
        '--max-time',
        default=None,
        type=float,
        help='Maximum Length of Simulation')
    argparser.add_argument(
        '--max-tasks',
        default=MAX_SERVICED_TASKS,
        type=int,
        help='Maximum number of Tasks to service')
    argparser.add_argument(
        '--sectors',
        default=1,
        type=int,
        help='Divide the environment into <N> sectors')
    argparser.add_argument(
        '--total-tasks',
        default=MAX_SERVICED_TASKS,
        type=int,
        help='Total number of tasks to create (>=max_tasks)')
    argparser.add_argument(
        '--record-data',
        action='store_true',
        help='Record data to disk as frames')
    argparser.add_argument(
        '--centralized',
        action='store_true',
        help='Set up one depot in the centre of the map')
    argparser.add_argument(
        '--show-sim',
        action='store_true',
        help='Display the simulation window')
    argparser.add_argument(
        '--eta-first',
        action='store_true', default=False,
        help='Force the eta-segment to start at 1')
    argparser.add_argument(
        '--multipass',
        action='store_true',
        help='Run the simulation over multiple lambda and seeds')
    argparser.add_argument(
        '--data-source',
        default=None,
        help='CSV file containing task locations. Durations/Distances are loaded from a companion file, <data-source root>.distances.csv.  If the distance file is unavailable, euclidean distances are used instead')

    args = argparser.parse_args()

    if args.multipass:
        multiple_sims(args)

    else:
        simulate(args)
