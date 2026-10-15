pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'eleven'
gnome = import('gnome')

blueprints = custom_target('blueprints',
  input: files(
    'shortcuts-dialog.blp',
    'window.blp',
    'pages/welcome.blp',
    'pages/disks.blp',
    'pages/installation.blp',
    'pages/failure.blp',
    'pages/success.blp',
    'pages/experimental.blp'
  ),
  output: '.',
  command: [find_program('blueprint-compiler'), 'batch-compile', '--minify', '@OUTPUT@', '@CURRENT_SOURCE_DIR@', '@INPUT@'],
)

gnome.compile_resources('eleven',
  'eleven.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
  dependencies: blueprints,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'eleven.in',
  output: 'eleven',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

service_sources = [
  'service/service.py',
  'service/config.py',
  'service/log.py',
  'service/partitioner.py'
]

page_sources = [
  'pages/welcome.py',
  'pages/disks.py',
  'pages/installation.py',
  'pages/success.py',
  'pages/failure.py',
  'pages/experimental.py'
]

eleven_sources = [
  '__init__.py',
  'main.py',
  'window.py',
]

eleven_sources += service_sources
eleven_sources += page_sources

install_data(eleven_sources, install_dir: moduledir)
