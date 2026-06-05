WHR="test_outputs/paper_salt_precipitation"
if [ ! -d "test_outputs" ]; then
    mkdir "test_outputs"
fi
if [ -d $WHR ]; then
    rm -rf $WHR
fi
mkdir "test_outputs/paper_salt_precipitation"
cp -r publications/Impact_of_Intermittency_on_Salt_Precipitation_During_CO2_Injection_2024_SPE/. $WHR
python3 $WHR/case1/run_simulations.py & python3 $WHR/case2/run_simulations.py & python3 $WHR/case3/run_simulations.py & python3 $WHR/case4/run_all.py & wait
