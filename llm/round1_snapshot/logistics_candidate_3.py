def h(state, goals):
    undelivered_packages = sum(1 for pkg in goals[0] if ('at', pkg, _) not in state)
    loaded_packages = sum(1 for pkg in state if ('in', pkg, _) in state)

    return undelivered_packages + loaded_packages * 2