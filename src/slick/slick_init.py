from sys import argv
import subprocess
from os import mkdir
import pandas as pd
from shutil import rmtree

from .create_basic_characteristics_table import create_basic_table
from .create_basic_characteristics_table import create_basic_table_tng_camels
from .create_cloudspercore_list import create_cloudspercore_list
from .create_jobscript import create_jobscript
from .read_config import parse_parameters


def init(config_file):
    config = parse_parameters(config_file)

    try:
        mkdir("./" + config["output_dir"])
    except:
        pass

    # Creates table with basic characteristics for all the clouds
    if not config["skip_basictable"]:
        try:
            mkdir("./" + config["basictable_dir"])
        except FileExistsError:
            pass
        except Exception as e:
            print(f"Could not make basic_table directory: {e}")
        if config["sim"] == 'SIMBA':
            create_basic_table(config)
        else: create_basic_table_tng_camels(config)

    if not config["skip_lumcalc"]:
        # Creates table with basic characteristics for all the clouds (if mode='total'), or for a sample of them (mode = 'randomize')
        n_clouds_per_core = config["n_clouds_per_core"]
        param_filename, max_lines = create_cloudspercore_list(config, n_clouds_per_core)

        # Creates slick_run_jobscript.sh
        create_jobscript(
            param_filename,
            max_lines,
            int(config["max_cores"]),
            config_file,
            config["sbatch"],
            config["module"],
        )

        # Creates the lim file with the header
        try:
            df = pd.DataFrame(
                {
                    "Galaxy_ID": [],
                    "Cloud_ID": [],
                    "Mcloud": [],
                    "Rcloud": [],
                    "Pressure": [],
                    "Metallicity": [],
                    "RadField": [],
                    "DMR": [],
                    "Redshift": [],
                    "H2_lcii": [],
                    "CO10": [],
                    "CO21": [],
                    "CO32": [],
                    "CO43": [],
                    "CO54": [],
                    "CO10_intTB": [],
                    "CO21_intTB": [],
                    "CO32_intTB": [],
                    "CO43_intTB": [],
                    "CO54_intTB": [],
                    "CI10": [],
                    "CI21": [],
                    "CO65": [],
                    "CO76": [],
                    "CO87": [],
                    "CO98": [],
                    "CO65_intTB": [],
                    "CO76_intTB": [],
                    "CO87_intTB": [],
                    "CO98_intTB": [],
                    "OI1": [],
                    "OI2": [],
                    "OI3": [],
                    "fH2": [],
                    "fH": [],
                    "fHp": [],
                    "fCO": [],
                    "fCp": [],
                    "fC": [],
                    "fO": [],
                    "fOHx": [],
                    "gas_temp": [],
                    "dust_temp": [],
                    "n_dens": [],
                    "col_dens": [],
                    "Mol_gas": [],
                    "CO10_areal_TB": [],
                    "Time": [],
                    "NZONES": [],
                    "Zones_Converged": [],
                }
            )
            df.to_csv(
                f"./{config['output_dir']}/lim_df.csv", index=False, overwrite=False
            )
        except:
            pass

    if not config["skip_run"]:
        subprocess.run(["sbatch", "slick_run_jobscript.sh"])
