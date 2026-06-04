WHR="test_outputs/co2_cyclic_injection"
if [ ! -d "test_outputs" ]; then
    mkdir "test_outputs"
fi
if [ -d $WHR ]; then
    rm -rf $WHR
fi
pyopmnearwell -i examples/co2.toml -o $WHR -m single
plopm -i $WHR/CO2 -v sgas -m gif -dpi 1000 -interval 50 -loop 1 -d 10,5 -yformat .0f -f 20 -cnum 6 -t "Cyclic injection" -save $WHR/co2_gas
