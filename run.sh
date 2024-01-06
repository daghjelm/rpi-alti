# Define the base paths as variables
BASE_DIR="/home/computemodule"
DOCUMENTS_DIR="${BASE_DIR}/Documents"
RPI_ALTI_DIR="${DOCUMENTS_DIR}/rpi-alti"
RPI_SOUNDS_DIR="${DOCUMENTS_DIR}/rpi-sounds"
RPI_MOVIES_DIR="${DOCUMENTS_DIR}/rpi-movies"

# Set the DISPLAY environment variable
export DISPLAY=:0

# Run the Python script with arguments
python3 "${RPI_ALTI_DIR}/main.py" -v="${RPI_MOVIES_DIR}/5NY_EKAR.mp4" -a="${RPI_SOUNDS_DIR}/EK.wav" -s=10 -t -p=5 -b=600 --diff=0.7 -i=1
