#!/usr/bin/env python3
"""Load the real GTK 2 event module and open its sound context; play nothing."""
from pathlib import Path
import os
import shlex
import subprocess
import tempfile

code = r'''
#include <gtk/gtk.h>
#include <canberra-gtk.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
  if (!gtk_init_check(&argc, &argv)) return 2;
  FILE *f = fopen("/proc/self/maps", "r");
  char line[2048]; int loaded = 0;
  while (f && fgets(line, sizeof(line), f))
    if (strstr(line, "/gtk-2.0/modules/libcanberra-gtk-module.so")) loaded = 1;
  if (f) fclose(f);
  ca_context *context = ca_gtk_context_get();
  int status = context ? ca_context_open(context) : -1;
  printf("GTK2 event module loaded: %s; sound context: %d\n", loaded ? "yes" : "no", status);
  return loaded && status == 0 ? 0 : 3;
}
'''
with tempfile.TemporaryDirectory(prefix='check-gtk2-sound-') as td:
    exe = str(Path(td) / 'check')
    flags = shlex.split(subprocess.check_output(['pkg-config', '--cflags', '--libs', 'gtk+-2.0', 'libcanberra-gtk'], text=True))
    result = subprocess.run(['gcc', '-x', 'c', '-o', exe, '-'] + flags, input=code, capture_output=True, text=True)
    if result.returncode:
        print(result.stderr)
        result.check_returncode()
    env = os.environ.copy()
    env['GTK_MODULES'] = 'canberra-gtk-module'
    result = subprocess.run([exe], env=env, text=True, capture_output=True)
    print(result.stdout, end='')
    if result.stderr:
        print(result.stderr)
    result.check_returncode()
    assert 'Failed to load module' not in result.stderr
    assert 'undefined symbol' not in result.stderr
