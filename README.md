# Multi Threading

Example Class
-------------

```python
import multithreading

class Demo(multithreading.MultiThread):
    def task(self, task):
        print(task)

```


Example Main
------------

```python
task_list = range(1, 3 + 1)

demo = Demo(task_list, threads=3)

# Start
demo.start()
```

Result

```
1
2
3
```

**OR**


```python
demo = Demo(threads=3)

# Start threads
demo.start_threads()

# Adding task to queue
demo.add_task(1)
demo.add_task(2)
demo.add_task(3)

# Wait until queue is empty
demo.join()

```

Result

```
1
2
3
```


Install
-------

```shell
$ pip install multithreading
```
