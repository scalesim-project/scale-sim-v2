import argparse

from scalesim.scale_sim import scalesim

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', metavar='Topology file', type=str,
                        default="../topologies/test.csv",
                        help="Path to the topology file"
                        )
    parser.add_argument('-c', metavar='Config file', type=str,
                        default="../configs/unit_tests/scale_test1.cfg",
                        help="Path to the config file"
                        )

    args = parser.parse_args()
    topology = args.t
    config = args.c

    s = scalesim(save_disk_space=False, verbose=True,
              config=config,
              topology=topology
              )
    s.run_scale(top_path='../test_runs')
