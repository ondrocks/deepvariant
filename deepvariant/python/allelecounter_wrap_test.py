# Copyright 2017 Google Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""Tests for AlleleCounter CLIF python wrappers."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function



from absl.testing import absltest

from third_party.nucleus.io import fasta
from third_party.nucleus.io import sam
from third_party.nucleus.util import ranges
from deepvariant import testdata

from deepvariant.protos import deepvariant_pb2
from deepvariant.python import allelecounter as _allelecounter


def setUpModule():
  testdata.init()


class WrapAlleleCounterTest(absltest.TestCase):

  def setUp(self):
    self.ref = fasta.RefFastaReader(testdata.CHR20_FASTA)
    self.size = 100
    self.region = ranges.make_range('chr20', 10000000, 10000000 + self.size)
    self.options = deepvariant_pb2.AlleleCounterOptions(
        partition_size=self.size)

  def test_wrap(self):
    allele_counter = _allelecounter.AlleleCounter(self.ref.get_c_reader(),
                                                  self.region, self.options)
    self._verify_allele_counter(allele_counter)

  def test_wrap_with_string_ref(self):
    ref_bases = self.ref.query(
        ranges.make_range(self.region.reference_name, self.region.start,
                          self.region.end + 128))
    allele_counter = _allelecounter.AlleleCounter.from_reference_bases(
        ref_bases, self.region, self.options)
    self._verify_allele_counter(allele_counter)

  def _verify_allele_counter(self, allele_counter):
    sam_reader = sam.SamReader(testdata.CHR20_BAM)
    reads = list(sam_reader.query(self.region))
    self.assertGreater(len(reads), 0)
    for read in reads:
      allele_counter.add(read)
    counts = allele_counter.counts()
    self.assertEqual(len(counts), self.size)


if __name__ == '__main__':
  absltest.main()
