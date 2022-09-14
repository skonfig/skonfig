import logging
import shutil
import sys

import cdist.config
import cdist.emulator
import cdist.integration


def run(skonfig_arguments):
    import skonfig.cdist.arguments
    cdist_arguments = skonfig.cdist.arguments.get(skonfig_arguments)
    if not cdist_arguments:
        return False
    import skonfig.cdist.configuration
    cdist_configuration = skonfig.cdist.configuration.get(cdist_arguments)
    if not cdist_configuration:
        return False
    target_host = cdist_arguments.host[0]
    cdist_config = cdist.config.Config
    cdist_config.construct_remote_exec_copy_patterns(cdist_arguments)
    base_root_path = cdist_config.create_base_root_path(None)
    host_base_path, hostdir = cdist_config.create_host_base_dirs(
        target_host, base_root_path
    )
    cdist_config._check_and_prepare_args(cdist_arguments)
    cdist_config.onehost(
        target_host,
        None,
        host_base_path,
        hostdir,
        cdist_arguments,
        parallel=False,
        configuration=cdist_configuration,
        remove_remote_files_dirs=(skonfig_arguments.verbose < 2),
    )
    shutil.rmtree(base_root_path)
    return True


def emulator():
    cdist.emulator.Emulator(sys.argv).run()
    return True
