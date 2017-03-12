from flask import Flask
from flask import render_template, abort, send_file, url_for
import os
import stat
import datetime
import time
import math

app = Flask('dirlist', instance_relative_config=True)
app.config.from_pyfile('config.py')


def human_time(*args, **kwargs):
    secs  = float(datetime.timedelta(*args, **kwargs).total_seconds())
#    units = [("day", 86400), ("hour", 3600), ("minute", 60), ("second", 1)]
    units = [("day", 86400), ("hour", 3600), ("minute", 60)]
    parts = []
    for unit, mul in units:
        if secs / mul >= 1 or mul == 1:
            if mul > 1:
                n = int(math.floor(secs / mul))
                secs -= n * mul
            else:
                n = secs if secs != int(secs) else int(secs)
            parts.append("%s %s%s" % (n, unit, "" if n == 1 else "s"))
    return " ".join(parts)

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>/')
def index(path):

    print('path is: ', path)
    realpath = os.path.join(app.config['ROOT_DIR'], path)
    filestats = list()
    is_dir = True
    now = time.time()
    try:
        filelist = os.listdir(realpath)
    except FileNotFoundError as e:
        return abort(404)
    except NotADirectoryError as e:
        is_dir = False
    if is_dir:
        for f in filelist:
            d = dict()
            s = os.stat(os.path.join(realpath, f))
            d['name'] = f
            d['human_size'] = sizeof_fmt(s.st_size)
            d['size'] = s.st_size
            d['dir'] = stat.S_ISDIR(s.st_mode)
            d['mtime'] = s.st_mtime
            d['human_mtime'] = human_time(seconds=(now - s.st_mtime))
            d['path'] = os.path.join(url_for('index') + path, f)
            filestats.append(d)
        return render_template('index.html', filestats=filestats, path=path)
    else:
        return send_file(realpath)

@app.route('/list/<path:path>')
def get_list(path):
    pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
