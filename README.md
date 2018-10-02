# CLIx
CLIx (CLI Explorer) let's you quickly discover new CLIs and versions.
CLIx can also help you generate new versions of your CLI interaction libraries.

**note:** CLIx will likely require a new parser for your project.
You can extend this functionality by creating your own parser class.

Installation
------------
```pip install .```
or
```python setup.py install```


Usage
-----
```usage: clix [-h] {explore,diff,makelib,list}```

CLI Exploration
---------------
Explore a target CLI, saving all entities, methods, and parameters to a version file.
If you don't specify a version, clix will save the results by date.

**Examples:**

```clix explore --help```

```clix explore -n hammer -t my.sathost.com -a admin/changeme -v 6.2.14 -p hammer```

```clix explore -n hammer -t my.sathost.com```

Version Diff
------------
clix can give you a diff between previously explored versions of an CLI.
This is more helpful than performing a linux-style diff on the file, since it retains context.
By default it will use the most recently explored CLI and the latest known versions (with dated version sorted to the bottom).

**Examples:**

```clix diff --help```

```clix diff -n hammer -l 6.3 -p 6.2.14```

```clix diff -n hammer -l 6.3```

```clix diff -n hammer```

```clix diff```

Library Maker
-------------
You can setup clix to populate any library you may be using to interact with your CLI.
You will have to provide template files, as well as extend clix's code base to populate those templates.
clix comes with the ability to populate a python library used for Satellite 6.
By default it will use the most recently explored CLI and the latest known versions (with dated version sorted to the bottom).

**Examples:**

```clix makelib --help```

```clix makelib -n hammer -v 6.3```

```clix makelib -n hammer```

```clix makelib```


List
----
clix can also list out the CLIs and versions for an CLI that is currently knows about.

**Examples:**

```clix list --help```

```clix list CLIs```

```clix list versions -n hammer```

Docker
------
clix is also available with automatic builds on dockerhub.
You can either pull down the latest, or a specific released version.
Additionally, you can build your own image locally. You will want to mount the local clix directory to keep any data clix creates.

**Examples:**

```docker build -t clix .```

```docker run -it clix explore --help```

```docker run -it -v $(pwd):/clix/:Z clix explore -n hammer -t my.sathost.com -v 6.2.14```

Note
----
This project only explicitly supports python 3.6+.
