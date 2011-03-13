from distutils.core import setup

setup(
      name="Archive organizer",
      url="http://www.osa1.net",
      author="Omer Sinan Agacan",
      author_email = "omeragacan@gmail.com",
      version="0.2",
      packages=["mutagen", "fsmonitor"],
      scripts=["watcher.py", "yeniduzenleyici.py"],
      license="MIT",
      long_description=open('README.rst').read(),
      )