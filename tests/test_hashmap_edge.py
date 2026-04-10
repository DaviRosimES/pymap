"""
test_hashmap_edge.py
====================
Fluxo de extensão – 10+ cenários cobrindo casos inoportunos / bordas do HashMap.
"""

import pytest
from unittest.mock import patch, MagicMock
from pymap import HashMap


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_map():
    hm = HashMap(capacity=4)
    hm.put("a", 1)
    hm.put("b", 2)
    return hm


# ---------------------------------------------------------------------------
# Cenário 1 – Remoção de chave inexistente
# ---------------------------------------------------------------------------

class TestRemoveErrors:
    def test_remove_missing_key_raises_key_error(self):
        hm = HashMap()
        with pytest.raises(KeyError):
            hm.remove("ghost")

    def test_remove_same_key_twice_raises_key_error(self, small_map):
        small_map.remove("a")
        with pytest.raises(KeyError):
            small_map.remove("a")

    def test_delitem_missing_key_raises_key_error(self):
        hm = HashMap()
        with pytest.raises(KeyError):
            del hm["missing"]


# ---------------------------------------------------------------------------
# Cenário 2 – Acesso com [] em chave ausente
# ---------------------------------------------------------------------------

class TestGetItemErrors:
    def test_getitem_missing_key_raises_key_error(self):
        hm = HashMap()
        with pytest.raises(KeyError):
            _ = hm["not_here"]

    def test_getitem_after_removal_raises_key_error(self, small_map):
        del small_map["b"]
        with pytest.raises(KeyError):
            _ = small_map["b"]


# ---------------------------------------------------------------------------
# Cenário 3 – Capacidade inválida
# ---------------------------------------------------------------------------

class TestInvalidCapacity:
    def test_zero_capacity_raises_value_error(self):
        with pytest.raises(ValueError):
            HashMap(capacity=0)

    def test_negative_capacity_raises_value_error(self):
        with pytest.raises(ValueError):
            HashMap(capacity=-5)


# ---------------------------------------------------------------------------
# Cenário 4 – Chaves não hashable
# ---------------------------------------------------------------------------

class TestUnhashableKeys:
    def test_list_as_key_raises_type_error(self):
        hm = HashMap()
        with pytest.raises(TypeError):
            hm.put([1, 2, 3], "value")

    def test_dict_as_key_raises_type_error(self):
        hm = HashMap()
        with pytest.raises(TypeError):
            hm.put({"a": 1}, "value")


# ---------------------------------------------------------------------------
# Cenário 5 – Colisões de hash (mock)
# ---------------------------------------------------------------------------

class TestHashCollisions:
    def test_collision_all_keys_still_accessible(self):
        """Simula colisões forçando todas as chaves para o mesmo bucket.
        
        O patch só é aplicado durante os puts. Após o with, o get() usa
        o _bucket_index real, mas como todas as chaves foram inseridas no
        bucket 0, usamos os buckets internos diretamente para validar o
        encadeamento (chaining).
        """
        hm = HashMap(capacity=8)
        with patch.object(hm, "_bucket_index", return_value=0):
            hm.put("x", 10)
            hm.put("y", 20)
            hm.put("z", 30)
        # Valida encadeamento: bucket 0 deve conter os 3 pares
        bucket_zero = hm._buckets[0]
        stored = dict(bucket_zero)
        assert stored["x"] == 10
        assert stored["y"] == 20
        assert stored["z"] == 30
        assert len(bucket_zero) == 3

    def test_collision_size_correct(self):
        hm = HashMap(capacity=8)
        with patch.object(hm, "_bucket_index", return_value=0):
            hm.put("p", 1)
            hm.put("q", 2)
        assert hm.size() == 2


# ---------------------------------------------------------------------------
# Cenário 6 – get() com valor None armazenado vs chave ausente
# ---------------------------------------------------------------------------

class TestNoneValueAmbiguity:
    def test_none_value_is_distinguishable_via_contains(self):
        """get() retorna None tanto para valor None quanto para chave ausente;
        contains() é o árbitro correto."""
        hm = HashMap()
        hm.put("key", None)
        assert hm.get("key") is None
        assert hm.contains("key") is True
        assert hm.contains("other") is False

    def test_default_not_returned_for_stored_none(self):
        hm = HashMap()
        hm.put("k", None)
        # get devolve None (o valor real), não o default
        result = hm.get("k", "FALLBACK")
        assert result is None


# ---------------------------------------------------------------------------
# Cenário 7 – Operações em mapa vazio
# ---------------------------------------------------------------------------

class TestOperationsOnEmptyMap:
    def test_keys_on_empty_map_returns_empty_list(self):
        assert HashMap().keys() == []

    def test_values_on_empty_map_returns_empty_list(self):
        assert HashMap().values() == []

    def test_items_on_empty_map_returns_empty_list(self):
        assert HashMap().items() == []

    def test_iter_on_empty_map_yields_nothing(self):
        assert list(HashMap()) == []


# ---------------------------------------------------------------------------
# Cenário 8 – Reinserção após remoção
# ---------------------------------------------------------------------------

class TestReinsertAfterRemove:
    def test_reinsert_after_remove_succeeds(self, small_map):
        small_map.remove("a")
        small_map.put("a", 999)
        assert small_map.get("a") == 999

    def test_size_correct_after_remove_and_reinsert(self, small_map):
        before = small_map.size()
        small_map.remove("b")
        small_map.put("b", 42)
        assert small_map.size() == before   # volta ao mesmo tamanho


# ---------------------------------------------------------------------------
# Cenário 9 – Estabilidade com grande volume de dados
# ---------------------------------------------------------------------------

class TestLargeDataVolume:
    def test_insert_and_retrieve_10000_entries(self):
        hm = HashMap()
        n = 10_000
        for i in range(n):
            hm.put(i, i ** 2)
        assert hm.size() == n
        for i in range(n):
            assert hm.get(i) == i ** 2

    def test_remove_all_entries_leaves_empty_map(self):
        hm = HashMap()
        keys = list(range(50))
        for k in keys:
            hm.put(k, k)
        for k in keys:
            hm.remove(k)
        assert hm.size() == 0
        assert hm.is_empty() is True


# ---------------------------------------------------------------------------
# Cenário 10 – Igualdade entre mapas
# ---------------------------------------------------------------------------

class TestEquality:
    def test_empty_maps_are_equal(self):
        assert HashMap() == HashMap()

    def test_map_not_equal_to_plain_dict(self):
        hm = HashMap()
        hm.put("a", 1)
        assert hm != {"a": 1}   # tipos diferentes → NotImplemented → False

    def test_map_not_equal_after_extra_key(self):
        a = HashMap()
        b = HashMap()
        a.put("x", 1)
        b.put("x", 1)
        b.put("y", 2)
        assert a != b


# ---------------------------------------------------------------------------
# Cenário 11 – Mock: validar que _rehash é chamado no threshold
# ---------------------------------------------------------------------------

class TestRehashTrigger:
    def test_rehash_called_when_load_factor_exceeded(self):
        hm = HashMap(capacity=4)
        with patch.object(hm, "_rehash", wraps=hm._rehash) as mock_rehash:
            # load_factor threshold = 0.75 → dispara no 4º item (4/4 = 1.0 > 0.75)
            for i in range(10):
                hm.put(f"k{i}", i)
            assert mock_rehash.call_count >= 1