import os
import sys
import platform
import shutil
import subprocess
import zipfile
import tarfile
from pathlib import Path
from urllib.request import urlretrieve
from typing import Optional

class FFmpegSetup:
    """Handles automatic FFmpeg detection and download"""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.ffmpeg_dir = Path(__file__).parent / "ffmpeg_bin"
        self.ffmpeg_path: Optional[Path] = None
        
    def is_ffmpeg_installed(self) -> bool:
        """Check if FFmpeg is installed on the system"""
        # First check system PATH
        ffmpeg_which = shutil.which('ffmpeg')
        if ffmpeg_which:
            self.ffmpeg_path = Path(ffmpeg_which)
            return True
        
        # Check local ffmpeg_bin directory
        if self.system == 'windows':
            local_ffmpeg = self.ffmpeg_dir / 'bin' / 'ffmpeg.exe'
        else:
            local_ffmpeg = self.ffmpeg_dir / 'ffmpeg'
            
        if local_ffmpeg.exists():
            self.ffmpeg_path = local_ffmpeg
            return True
            
        return False
    
    def get_download_url(self) -> str:
        """Get the appropriate FFmpeg download URL based on OS and architecture"""
        if self.system == 'windows':
            # Using FFmpeg builds from gyan.dev (Windows)
            return "https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-essentials_build.zip"
        
        elif self.system == 'linux':
            # Using FFmpeg builds from johnvansickle.com (Linux static builds)
            if 'x86_64' in self.machine or 'amd64' in self.machine:
                return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            elif 'arm' in self.machine or 'aarch64' in self.machine:
                return "https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
            else:
                raise Exception(f"Unsupported Linux architecture: {self.machine}")
        
        elif self.system == 'darwin':
            # For macOS, we'll use static builds
            if 'arm' in self.machine or 'aarch64' in self.machine:
                # M1/M2/M3 Macs
                return "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
            else:
                # Intel Macs
                return "https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip"
        
        else:
            raise Exception(f"Unsupported operating system: {self.system}")
    
    def download_progress_hook(self, block_num, block_size, total_size):
        """Progress bar for download"""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100.0 / total_size, 100)
            sys.stdout.write(f"\rDownloading FFmpeg: {percent:.1f}%")
            sys.stdout.flush()
    
    def download_ffmpeg(self):
        """Download FFmpeg for the current platform"""
        print(f"FFmpeg not found. Downloading for {self.system} ({self.machine})...")
        
        # Create ffmpeg directory
        self.ffmpeg_dir.mkdir(exist_ok=True)
        
        # Get download URL
        url = self.get_download_url()
        
        # Determine file extension
        if url.endswith('.zip'):
            archive_path = self.ffmpeg_dir / 'ffmpeg.zip'
        elif url.endswith('.tar.xz'):
            archive_path = self.ffmpeg_dir / 'ffmpeg.tar.xz'
        else:
            archive_path = self.ffmpeg_dir / 'ffmpeg.zip'
        
        # Download
        try:
            urlretrieve(url, archive_path, reporthook=self.download_progress_hook)
            print("\n✓ Download complete!")
        except Exception as e:
            raise Exception(f"Failed to download FFmpeg: {e}")
        
        # Extract
        print("Extracting FFmpeg...")
        self.extract_archive(archive_path)
        
        # Clean up archive
        archive_path.unlink()
        
        print("✓ FFmpeg setup complete!")
    
    def extract_archive(self, archive_path: Path):
        """Extract the downloaded archive"""
        if archive_path.suffix == '.zip':
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(self.ffmpeg_dir)
            
            # For Windows, move ffmpeg.exe to the right location
            if self.system == 'windows':
                # Find ffmpeg.exe in extracted folders
                for root, dirs, files in os.walk(self.ffmpeg_dir):
                    if 'ffmpeg.exe' in files:
                        src = Path(root) / 'ffmpeg.exe'
                        dest_dir = self.ffmpeg_dir / 'bin'
                        dest_dir.mkdir(exist_ok=True)
                        dest = dest_dir / 'ffmpeg.exe'
                        shutil.move(str(src), str(dest))
                        self.ffmpeg_path = dest
                        break
            
            # For macOS (zip from evermeet.cx)
            elif self.system == 'darwin':
                ffmpeg_file = self.ffmpeg_dir / 'ffmpeg'
                if ffmpeg_file.exists():
                    os.chmod(ffmpeg_file, 0o755)
                    self.ffmpeg_path = ffmpeg_file
        
        elif archive_path.suffix == '.xz':
            with tarfile.open(archive_path, 'r:xz') as tar_ref:
                tar_ref.extractall(self.ffmpeg_dir)
            
            # For Linux, find and move ffmpeg binary
            for root, dirs, files in os.walk(self.ffmpeg_dir):
                if 'ffmpeg' in files:
                    src = Path(root) / 'ffmpeg'
                    dest = self.ffmpeg_dir / 'ffmpeg'
                    if src != dest:
                        shutil.move(str(src), str(dest))
                    os.chmod(dest, 0o755)
                    self.ffmpeg_path = dest
                    break
    
    def setup(self) -> Path:
        """Main setup method - checks for FFmpeg and downloads if needed"""
        if not self.is_ffmpeg_installed():
            self.download_ffmpeg()
        else:
            print(f"✓ FFmpeg found at: {self.ffmpeg_path}")
        
        if self.ffmpeg_path is None:
            raise Exception("Failed to set up FFmpeg")
        
        return self.ffmpeg_path
    
    def get_ffmpeg_command(self) -> str:
        """Get the FFmpeg command to use (system or local)"""
        if self.ffmpeg_path:
            return str(self.ffmpeg_path)
        elif self.is_ffmpeg_installed():
            return str(self.ffmpeg_path)
        else:
            raise Exception("FFmpeg not found and failed to download")


def ensure_ffmpeg() -> str:
    """Convenience function to ensure FFmpeg is available"""
    setup = FFmpegSetup()
    setup.setup()
    return setup.get_ffmpeg_command()


if __name__ == "__main__":
    # Test the setup
    try:
        ffmpeg_cmd = ensure_ffmpeg()
        print(f"\nFFmpeg command: {ffmpeg_cmd}")
        
        # Test FFmpeg
        result = subprocess.run([ffmpeg_cmd, '-version'], 
                              capture_output=True, text=True)
        print("\nFFmpeg version info:")
        print(result.stdout.split('\n')[0])
    except Exception as e:
        print(f"Error: {e}")
