from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_platform.clustering import cluster_failures
from verification_platform.triage import Failure


def test_duplicate_failures_form_one_actionable_cluster():
    clusters = cluster_failures([Failure(1, "q", "0", "1"), Failure(8, "q", "0", "1"), Failure(2, "d", "1", "0")])
    assert len(clusters) == 2
    assert [item.cycle for item in clusters["q:0->1"]] == [1, 8]
