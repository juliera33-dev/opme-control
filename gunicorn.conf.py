import multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'
bind = '0.0.0.0:' + str(os.environ.get('PORT', '8080'))
timeout = 120
keepalive = 5