# Copyright (c) 2010 Advanced Micro Devices, Inc.
#               2016 Georgia Institute of Technology
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Authors: Brad Beckmann
#          Tushar Krishna

from m5.params import *
from m5.objects import *

from BaseTopology import SimpleTopology

# Creates a generic Mesh assuming an equal number of cache
# and directory controllers.
# XY routing is enforced (using link weights)
# to guarantee deadlock freedom.

class HeterogeneousMesh(SimpleTopology):
    description='HeterogeneousMesh'

    print "Creating Topology: " + description

    def __init__(self, controllers):
        self.nodes = controllers

    # Makes a generic mesh
    # assuming an equal number of cache and directory cntrls

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes

        num_routers = options.num_cpus
        num_rows = options.mesh_rows

        # default values for link latency and router latency.
        # Can be over-ridden on a per link/router basis
        link_latency = options.link_latency # used by simple and garnet
        router_latency = options.router_latency # only used by garnet


        # There must be an evenly divisible number of cntrls to routers
        # Also, obviously the number or rows must be <= the number of routers
        cntrls_per_router, remainder = divmod(len(nodes), num_routers)
        assert(num_rows > 0 and num_rows <= num_routers)
        num_columns = int(num_routers / num_rows)
        assert(num_columns * num_rows == num_routers)

        # Create the routers in the mesh
        routers = [Router(router_id=i, latency = router_latency) \
            for i in range(num_routers)]
        network.routers = routers

        # link counter to set unique link ids
        link_count = 0

        # Add all but the remainder nodes to the list of nodes to be uniformly
        # distributed across the network.
        network_nodes = []
        remainder_nodes = []
        for node_index in xrange(len(nodes)):
            if node_index < (len(nodes) - remainder):
                network_nodes.append(nodes[node_index])
            else:
                remainder_nodes.append(nodes[node_index])

        # Connect each node to the appropriate router
        ext_links = []
        for (i, n) in enumerate(network_nodes):
            cntrl_level, router_id = divmod(i, num_routers)
            assert(cntrl_level < cntrls_per_router)
            ext_links.append(ExtLink(link_id=link_count, ext_node=n,
                                    int_node=routers[router_id],
                                    latency = link_latency))
            link_count += 1

        # Connect the remainding nodes to router 0.  These should only be
        # DMA nodes.
        for (i, node) in enumerate(remainder_nodes):
            assert(node.type == 'DMA_Controller')
            assert(i < remainder)
            ext_links.append(ExtLink(link_id=link_count, ext_node=node,
                                    int_node=routers[0],
                                    latency = link_latency))
            link_count += 1

        network.ext_links = ext_links

        # Create the mesh links.
        int_links = []

        # East output to West input links (weight = 1)
        for row in xrange(num_rows):
            for col in xrange(num_columns):
                #from left to right
                if (col + 1 < num_columns and col!=1):
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    print "Router " + get_id(routers[east_out]) + " created a link to Router " +  get_id(routers[west_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[east_out],
                                             dst_node=routers[west_in],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency = link_latency,
                                             weight=1))
                    link_count += 1

                if((col == 1) and (row == 1 or row == 2)):
                    east_out = col + (row * num_columns)
                    west_in = (col + 1) + (row * num_columns)
                    print "Router " + get_id(routers[east_out]) + " created a link to Router " + get_id(routers[west_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[east_out],
                                             dst_node=routers[west_in],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency=link_latency,
                                             weight=1))

                    left = col + (row * num_columns)
                    right = (col + 1) + (row * num_columns)
                    print "Router " + get_id(routers[left]) + " created a link to Router " + get_id(routers[right])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[left],
                                             dst_node=routers[right],
                                             src_outport="East",
                                             dst_inport="West",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 2





        # West output to East input links (weight = 1)
        for row in xrange(num_rows):
            for col in xrange(num_columns):
                if (col + 1 < num_columns and col !=1):
                    #right to left
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    print "Router " + get_id(routers[west_out]) + " created a link to Router " +  get_id(routers[east_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[west_out],
                                             dst_node=routers[east_in],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency = link_latency,
                                             weight=1))
                    link_count += 1
                if ((col == 1) and (row == 1 or row == 2)):
                    #right to left
                    left = col + (row * num_columns)
                    right = (col + 1) + (row * num_columns)
                    print "Router " + get_id(routers[right]) + " created a link to Router " +  get_id(routers[left])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[right],
                                             dst_node=routers[left],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency = link_latency,
                                             weight=1))
                    # right to left
                    east_in = col + (row * num_columns)
                    west_out = (col + 1) + (row * num_columns)
                    
                    print "Router " + get_id(routers[west_out]) + " created a link to Router " + get_id(routers[east_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[west_out],
                                             dst_node=routers[east_in],
                                             src_outport="West",
                                             dst_inport="East",
                                             latency=link_latency,
                                             weight=1))
                    link_count += 2




        # North output to South input links (weight = 2)
        for col in xrange(num_columns):
            for row in xrange(num_rows):
                #from down to up
                if (row + 1 < num_rows and row!=1):
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    print "Router " + get_id(routers[north_out]) + " created a link to Router " +  get_id(routers[south_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north_out],
                                             dst_node=routers[south_in],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency = link_latency,
                                             weight=2))
                    link_count += 1
                if ((row == 1) and (col == 1 or col == 2)):
                    #down to up
                    north_out = col + (row * num_columns)
                    south_in = col + ((row + 1) * num_columns)
                    print "Router " + get_id(routers[north_out]) + " created a link to Router " +  get_id(routers[south_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[north_out],
                                             dst_node=routers[south_in],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency = link_latency,
                                             weight=2))
                    down = col + (row * num_columns)
                    up = col + ((row + 1) * num_columns)
                    print "Router " + get_id(routers[down]) + " created a link to Router " + get_id(routers[up])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[down],
                                             dst_node=routers[up],
                                             src_outport="North",
                                             dst_inport="South",
                                             latency=link_latency,
                                             weight=2))
                    link_count += 2

        # South output to North input links (weight = 2)
        for col in xrange(num_columns):
            for row in xrange(num_rows):
                # from up to down
                if (row + 1 < num_rows and row!=1):
                    north_in = col + (row * num_columns)
                    south_out = col + ((row + 1) * num_columns)
                    # print("test1")
                    print "Router " + get_id(routers[south_out]) + " created a link to Router " +  get_id(routers[north_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[south_out],
                                             dst_node=routers[north_in],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency = link_latency,
                                             weight=2))
                    link_count += 1
                    
                if ((row == 1) and (col == 1 or col == 2)):
                    #down one
                    north_in = col + (row * num_columns)
                    #up one
                    south_out = col + ((row + 1) * num_columns)
                    # print("test2")
                    # from down to up
                    print "Router " + get_id(routers[south_out]) + " created a link to Router " +  get_id(routers[north_in])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[south_out],
                                             dst_node=routers[north_in],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency = link_latency,
                                             weight=2))
                    
                    down = col + (row * num_columns)
                    up = col + ((row + 1) * num_columns)
                    print "Router " + get_id(routers[up]) + " created a link to Router " + get_id(routers[down])
                    int_links.append(IntLink(link_id=link_count,
                                             src_node=routers[up],
                                             dst_node=routers[down],
                                             src_outport="South",
                                             dst_inport="North",
                                             latency=link_latency,
                                             weight=2))
                    link_count +=2


        network.int_links = int_links

def get_id(node) :
    return str(node).split('.')[3].split('routers')[1]
