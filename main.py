import logging
import matplotlib
from book_generator.orchestrator import run_generation_process

if __name__ == "__main__":
    # Configure Matplotlib to use LaTeX and load amsmath
    matplotlib.rcParams["text.usetex"] = True
    matplotlib.rcParams["text.latex.preamble"] = (
        r"\usepackage{amsmath}  \usepackage{amssymb}"
    )

    # Ensure matplotlib doesn't try to use a GUI backend
    matplotlib.pyplot.switch_backend("Agg")

    # Configure logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    run_generation_process()
