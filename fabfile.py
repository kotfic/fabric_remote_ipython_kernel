from fabric.api import env, run, local, task
import os


@task
def launch_kernel():
    IPYTHON = run("which ipython")

    env['tmux_session'] = "kernel_{}".format(os.getpid())

    env['kernel_file'] = "{tmux_session}.json".format(**env)
    env['kernel_path'] = "/tmp/{kernel_file}".format(**env)
    env['kernel_cmd'] = IPYTHON + " kernel \
    --IPKernelApp.connection_file={kernel_path}".format(**env)

    run("""
    tmux new-session -d -s {tmux_session} "{kernel_cmd}"
    while  [  ! -f {kernel_path} ]; do sleep 1s; done
    """.format(**env))

    env['local_kernel_path'] = "/tmp/{kernel_file}".format(**env)
    local("scp {user}@{host}:{kernel_path} {local_kernel_path}".format(**env))


@task
def connect(console_type):
    if console_type == "console":
        local("ipython console "
              "--existing {local_kernel_path} "
              "--ssh {user}@{host}".format(console_type=console_type, **env))
    else:
        local("ipython qtconsole "
              "--existing {local_kernel_path} "
              "--stylesheet=~/bin/.remote_kernel/tomorrow-night.css "
              "--IPythonWidget.font_size=12  "
              "--IPythonQtConsoleApp.hide_menubar=True "
              "--ssh {user}@{host}".format(console_type=console_type, **env))


@task
def kill_kernel():
    # Clean up
    run("tmux kill-session -t {tmux_session}".format(**env))
    local('rm {local_kernel_path}'.format(**env))


@task
def launch(console_type):
    launch_kernel()
    connect(console_type)
    kill_kernel()
