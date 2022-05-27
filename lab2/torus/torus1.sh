for i in $(seq 0.02 0.02 2.02) ;
 
do
./build/Garnet_standalone/gem5.opt configs/example/garnet_synth_traffic.py --network=garnet2.0 --num-cpus=16 --num-dirs=16 --topology=Mesh_XY --mesh-rows=4 --sim-cycles=50000 --inj-vnet=0 --router-latency=2  --injectionrate=$i --synthetic=uniform_random --link-width-bits=32
./my_scripts/extract_network_stats.sh
cat network_stats.txt >> uniform.txt 
done
