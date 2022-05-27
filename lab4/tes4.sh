./build/RISCV_MESI_Two_Level/gem5.fast --outdir my_STATS/RISCV_64c_MESI_Radii-L1-1kB_L2_"$1"kB_VC-"$2"-tr-"$3" configs/example/se.py --cpu-type=TimingSimpleCPU --num-cpus=16 --num-l2caches=16  --l1d_size=1kB  --l1i_size=1kB  --l1d_assoc=2  --l1i_assoc=2  --l2_size="$1"kB --l2_assoc=8  --num-dirs=4  --mem-size=4096MB --ruby --network=garnet2.0 --topology=MeshDirCorners_XY --mesh-rows=4 --vcs-per-vnet=$2 --router-latency=$3 --maxinsts=100000 -c my_benchmarks/ligra/bin/riscv/Radii -o '-n 16 my_benchmarks/ligra/input/rMatGraph_J_5_100'
