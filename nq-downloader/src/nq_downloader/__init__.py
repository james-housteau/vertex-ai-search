"""Natural Questions dataset downloader."""

__version__ = "0.1.0"

# Import main classes for easy access
from .downloader import NQDownloader, DownloadResult

__all__ = ["NQDownloader", "DownloadResult", "__version__"]
