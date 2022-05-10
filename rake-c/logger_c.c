/*
 * Copyright (c) 2020 rxi
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 * 
 * Adapted by Tom Nguyen for CITS3002-project 2022
 */

#include "logger_c.h"

#define MAX_CALLBACKS   32

typedef struct {
    log_LogFn fn;
    void *udata;
    int level;
} Callback;

static struct {
    void *udata;
    int level;
    bool quiet;
    Callback callbacks[MAX_CALLBACKS];
} L;

static const char *level_strings[] = {
    "TRACE", "DEBUG", "INFO", "WARN", "ERROR", "FATAL"
};

static void stdout_callback(log_Event *ev) {
    char buffer[16];
    buffer[strftime(buffer, sizeof(buffer), "%H:%M:%S", ev->time)] = '\0';
    fprintf(ev->udata, "%s %-5s %s:%d: ",
            buffer, level_strings[ev->level], ev->file, ev->line);
    vfprintf(ev->udata, ev->fmt, ev->ap);
    fprintf(ev->udata, "\n");
    fflush(ev->udata);
}

static void file_callback(log_Event *ev) {
    char buffer[64];
    buffer[strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M:%S", ev->time)] = '\0';
    fprintf(ev->udata, "%s %-5s %s:%d:",
            buffer, level_strings[ev->level], ev->file, ev->line);
    vfprintf(ev->udata, ev->fmt, ev->ap);
    fprintf(ev->udata, "\n");
    fflush(ev->udata);
}

const char *log_level_string(int level) {
    return level_strings[level];
}

void log_set_level(int level) {
    L.level = level;
}

void log_set_quiet(bool enable) {
    L.quiet = enable;
}

int log_add_callback(log_LogFn fn, void *udata, int level) {
    for (int i = 0; i < MAX_CALLBACKS; i++) {
        if (!L.callbacks[i].fn) {
            L.callbacks[i] = (Callback) { fn, udata, level };
            return 0;
        }
    }
    return -1;
}

int log_add_fp(FILE *fp, int level) {
    return log_add_callback(file_callback, fp, level);
}

static void init_event(log_Event *ev, void *udata) {
    if (!ev->time) {
        time_t t = time(NULL);
        ev->time = localtime(&t);
    }
    ev->udata = udata;

    //TODO get hostnaem and ip
    // char *IPbuffer;
    // char hostbuffer[256];
    // struct hostent *host_entry;
    // gethostname(hostbuffer, sizeof(hostbuffer));
    // strcpy(ev->hostname, hostbuffer);
    // host_entry = gethostbyname(ev->hostname);
    // IPbuffer = inet_ntoa(*((struct in_addr*)
    //                        host_entry->h_addr_list[0]));

    // strcpy(ev->ip, IPbuffer);
}

void log_log(int level, const char *file, int line, const char *fmt, ...) {
    log_Event ev = {
        .fmt   = fmt,
        .file  = file,
        .line  = line,
        .level = level,
    };

  if (!L.quiet && level >= L.level) {
            init_event(&ev, stderr);
            va_start(ev.ap, fmt);
            stdout_callback(&ev);
            va_end(ev.ap);
    }

  for (int i = 0; i < MAX_CALLBACKS && L.callbacks[i].fn; i++) {
        Callback *cb = &L.callbacks[i];
        if (level >= cb->level) {
            init_event(&ev, cb->udata);
            va_start(ev.ap, fmt);
            cb->fn(&ev);
            va_end(ev.ap);
        }
    }

}
