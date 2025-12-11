#!/Users/howes/bin/python3

# Requires:
#   PyGithub==2.1.1
#   termcolor==2.4.0

import concurrent.futures
from concurrent.futures import Future
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from functools import partial
from github import Github
from github.Workflow import Workflow
from github.PaginatedList import PaginatedList
from termcolor import colored
from typing import Optional
import os
import re
import sys


class State(IntEnum):
  failed = 0
  pending = 1
  ok = 2

  def status(self) -> str:
    if self.value == 0:
      return colored('FAILED', 'red')
    elif self.value == 1:
      return colored('PENDING', 'yellow')
    else:
      return colored('OK', 'green')

  @staticmethod
  def from_conclusion(conclusion: Optional[str]) -> 'State':
    if conclusion == 'success':
      return State.ok
    if conclusion is None:
      return State.pending
    return State.failed


@dataclass
class Status:
  repo: str
  when: datetime
  state: State

  def show(self, max_name_length: int):
    status = self.state.status()
    dots = colored('.', 'light_blue') * (max_name_length - len(self.repo) + 2)
    print(self.repo + dots + status)

  def __lt__(self, other: 'Status') -> bool:
    return self.repo.lower() < other.repo.lower()


def run(gh_token: str) -> None:
  results: list[Status] = []
  pattern = re.compile(sys.argv[1]) if len(sys.argv) > 1 else None

  with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:

    def workflows_fut_done(fut: Future[PaginatedList[Workflow]], repo):
      for flow in list(fut.result()):
        if flow.name == 'CI':
          for run in flow.get_runs():
            results.append(Status(repo.name, run.created_at, State.from_conclusion(run.conclusion)))
            print(".", end='', flush=True)
            break
          break

    gh = Github(gh_token)
    for repo in gh.get_user().get_repos():
      if pattern and not pattern.search(repr(repo)):
        continue
      get_workflows_fut = executor.submit(repo.get_workflows)
      get_workflows_fut.add_done_callback(partial(workflows_fut_done, repo=repo))

  if not results:
    print('*** nothing found')
    return

  print('')
  max_name_width = max([len(r.repo) for r in results])
  for result in sorted(results):
    result.show(max_name_width)


if __name__ == '__main__':
  gh_token = os.environ.get('GITHUB_TOKEN')
  if gh_token is None:
    print("*** GITHUB_TOKEN is undefined")
    sys.exit(1)
    
  run(gh_token)
