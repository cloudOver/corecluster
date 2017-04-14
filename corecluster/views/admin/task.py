from corecluster.cache.task import Task
from corecluster.cache import Cache
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import HttpResponse, render_to_response
import simplejson

@staff_member_required
def graph(request):
    keys = Cache.hkeys(Task.container)
    tasks = [simplejson.loads(Cache.hget(Task.container, k)) for k in keys]
    resp = HttpResponse(simplejson.dumps(tasks, indent=2))
    resp['Content-type'] = 'application/json'
    return resp


@staff_member_required
def task_list(request):
    keys = Cache.hkeys(Task.container)
    tasks = [simplejson.loads(Cache.hget(Task.container, k)) for k in keys]

    task_objects = []
    for task in tasks:
        t = Task(id=task['id'], type=task['type'])
        task['blockers'] = Cache.lrange('blockers:' + t.cache_key(), 0, Cache.llen('blockers:' + t.cache_key()))
        task_objects.append(task)
    return render_to_response('admin_site/task_list.html', {'tasks': task_objects})
