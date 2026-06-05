WHR="test_outputs/hello_world"
if [ ! -d "test_outputs" ]; then
    mkdir "test_outputs"
fi
if [ -d $WHR ]; then
    rm -rf $WHR
fi
pyopmnearwell -i examples/h2o.toml -o $WHR -m single
plopm -i $WHR/H2O -v pressure -s ,,1 -t 'Top view at the end of the simulation' -c bwr -xformat .0f -cformat .0f -save $WHR/hello_world
