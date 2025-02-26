# AI Background Removal Service Deployment

This README contains instructions for deploying the AI Background Removal tool as a service on a Linux server.

## System Setup and Requirements

### 1. Update Server Packages

First, update the system packages:

```bash
# Update package lists
sudo apt-get update

# Upgrade installed packages
sudo apt-get upgrade -y

# Install required system dependencies
sudo apt-get install -y build-essential software-properties-common git wget
```

### 2. Install Python

Install Python 3.8+ if not already installed:

```bash
# Add deadsnakes PPA for newer Python versions
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update

# Install Python 3.9 and dev packages
sudo apt-get install -y python3 python3-dev python3-venv python3-pip
```

### 3. Install CUDA (if needed)

If CUDA is not already installed, follow the NVIDIA instructions for your specific distribution.
Example for Ubuntu 20.04 with CUDA 11.8:

```bash
# Install CUDA repository
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get install -y cuda
```

## Application Setup

### 1. Clone Repository & Setup Environment

Clone the repository and set up the Python environment:

```bash
# Navigate to the designated directory
cd /home/beepstream_visioblock/

# Clone the repository
git clone https://github.com/Reynold97/Background-Removal.git
# Or if the repository is not on GitHub:
# git clone [your-git-repo-url]

# If you don't have a Git repository, create the directory
# mkdir -p Background-Removal

cd Background-Removal

# Create a virtual environment
python3 -m venv env

# Activate the virtual environment
source env/bin/activate
```

### 2. Install Dependencies

Install required Python packages:

```bash
# Upgrade pip
pip install --upgrade pip

# If you have a requirements.txt file
pip install -r requirements.txt

# If requirements.txt isn't available, install the necessary packages
# pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu118
# pip install gradio transformers Pillow
```

### 3. Create a Systemd Service for Auto-start

Create a systemd service file to run the application as a service:

```bash
# Use nano to create the service file
sudo nano /etc/systemd/system/background-removal.service
```

Copy this 

```bash
[Unit]
Description=AI Background Removal Service
After=network.target

[Service]
User=beepstream_visioblock
Group=beepstream_visioblock
WorkingDirectory=/home/beepstream_visioblock/Background-Removal
ExecStart=/home/beepstream_visioblock/Background-Removal/env/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 4. Enable and Start the Service

Enable and start the service to run on boot:

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable background-removal.service

# Start the service
sudo systemctl start background-removal.service

# Check the status
sudo systemctl status background-removal.service
```

### 5. Configure Service to Run on a Specific Port (Optional)

If you need to change the default port (8080), modify the launch parameters in app.py:

```python
# Change this line at the bottom of app.py
demo.launch(show_error=True, server_port=YOUR_PORT, show_api=False)
```

## Monitoring & Management

### Logs and Status

To view the logs of the running service:

```bash
# Check the service status
sudo systemctl status background-removal.service

# View the logs
sudo journalctl -u background-removal.service -f
```

### Service Management

```bash
# Restart the service
sudo systemctl restart background-removal.service

# Stop the service
sudo systemctl stop background-removal.service 

# Start the service
sudo systemctl start background-removal.service
```

### Manual Start (For Testing)

If you want to manually start the application for testing:

```bash
cd /home/beepstream_visioblock/Background-Removal
source env/bin/activate
python app.py
```

## Troubleshooting

1. **Service fails to start**:
   - Check the logs: `sudo journalctl -u background-removal.service -f`
   - Verify CUDA is available: `python -c "import torch; print(torch.cuda.is_available())"`
   - Ensure all dependencies are installed correctly

2. **Permission issues**:
   - Ensure the user has appropriate permissions:
   ```bash
   sudo chown -R beepstream_visioblock:beepstream_visioblock /home/beepstream_visioblock/Background-Removal
   ```

3. **Model download issues**:
   - If the model fails to download automatically, manually download it:
   ```bash
   mkdir -p ~/.cache/huggingface/hub/
   cd ~/.cache/huggingface/hub/
   # Then follow instructions on the Hugging Face model page to download ZhengPeng7/BiRefNet
   ```

4. **GPU memory issues**:
   - If you encounter GPU memory errors, you can modify the app to use a smaller batch size or resize to smaller dimensions.