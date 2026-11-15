import pytest
import torch
from helix_pro import HELIXPro, create_helix_pro

class TestHELIXPro:
    def test_init(self):
        m = HELIXPro(dim=256, hidden_dim=512)
        assert m.dim == 256
    
    def test_forward(self):
        m = HELIXPro(dim=256)
        x = torch.randn(32, 256)
        assert m(x).shape == (32, 256)
    
    def test_factory(self):
        m = create_helix_pro()
        assert isinstance(m, HELIXPro)

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
