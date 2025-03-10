/**
 * Wrapper to set up pledge(2)/unveil(2) sandbox.
 *
 * 2025 Dennis Camera (dennis.camera at riiengineering.ch)
 *
 * This file is part of skonfig.
 *
 * skonfig is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * skonfig is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with skonfig. If not, see <http://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#define S_NONEMPTY(s) (s && *s)

#ifndef DEBUG
#define DEBUG 0
#endif

void do_pledge(const char *promises, const char *execpromises) {
#if DEBUG
	if (S_NONEMPTY(promises)) printf("pledge promises: %s\n", promises);
	if (S_NONEMPTY(execpromises)) printf("pledge execpromises: %s\n", execpromises);
#endif
	if (pledge(promises, execpromises)) {
		perror("pledge");
		exit(1);
	}
}

void do_unveil(const char *path, const char *permissions) {
#if DEBUG
	if (path != NULL || permissions != NULL) {
		printf("unveil %s (%s)\n", path, permissions);
	} else {
		printf("unveil locked\n");
	}
#endif
	if (unveil(path, permissions)) {
		perror("unveil");
		exit(1);
	}
}

int main(int argc, char **argv) {
	if (2 > argc) { return 0; }

	/* unveil */
	do_unveil("/", "rx");

	const char *tmpdir = getenv("TMPDIR");
	if (!tmpdir || !*tmpdir) {
		tmpdir = "/tmp";
	}
	do_unveil(tmpdir, "rwxc");

	const char *cache_home = getenv("XDG_CACHE_HOME");
	if (S_NONEMPTY(cache_home)) {
		do_unveil(cache_home, "rwxc");
	}

	do_unveil(NULL, NULL);  /* lock unveil() */

	/* pledge */
	const char *promises = "cpath error exec fattr flock proc prot_exec rpath stdio tmppath wpath";
	do_pledge(NULL, promises);

	/* run command */
	execvp(argv[1], &argv[1]);
	return -1;
}
