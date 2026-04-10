"""
test_hashmap_normal.py
======================
Fluxo normal – 10 cenários cobrindo o comportamento esperado do HashMap.
"""

import pytest
from pymap import HashMap


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_map():
    """HashMap vazio com capacidade padrão."""
    return HashMap()


@pytest.fixture
def populated_map():
    """HashMap pré-populado com 5 pares."""
    hm = HashMap()
    hm.put("name", "Alice")
    hm.put("age", 30)
    hm.put("city", "São Paulo")
    hm.put("score", 9.5)
    hm.put("active", True)
    return hm


# ---------------------------------------------------------------------------
# Cenário 1 – Inserção e recuperação simples
# ---------------------------------------------------------------------------

class TestPutAndGet:
    def test_put_single_key_value(self, empty_map):
        """Deve armazenar e recuperar um par simples."""
        empty_map.put("language", "Python")
        assert empty_map.get("language") == "Python"

    def test_put_integer_key(self, empty_map):
        """Chaves inteiras devem funcionar normalmente."""
        empty_map.put(42, "resposta")
        assert empty_map.get(42) == "resposta"

    def test_put_tuple_key(self, empty_map):
        """Chaves do tipo tuple (hashable) devem ser aceitas."""
        empty_map.put((1, 2), "ponto")
        assert empty_map.get((1, 2)) == "ponto"

    def test_get_returns_default_for_missing_key(self, empty_map):
        """get() com chave ausente deve retornar o default (None)."""
        assert empty_map.get("inexistente") is None

    def test_get_returns_custom_default(self, empty_map):
        """get() deve retornar o default customizado quando a chave não existe."""
        assert empty_map.get("x", -1) == -1


# ---------------------------------------------------------------------------
# Cenário 2 – Atualização de valor
# ---------------------------------------------------------------------------

class TestUpdate:
    def test_overwrite_existing_key(self, populated_map):
        """put() em chave existente deve atualizar o valor, não duplicar."""
        populated_map.put("name", "Bob")
        assert populated_map.get("name") == "Bob"

    def test_size_unchanged_after_overwrite(self, populated_map):
        """size() não deve crescer ao sobrescrever uma chave existente."""
        before = populated_map.size()
        populated_map.put("age", 31)
        assert populated_map.size() == before


# ---------------------------------------------------------------------------
# Cenário 3 – Remoção
# ---------------------------------------------------------------------------

class TestRemove:
    def test_remove_existing_key_returns_value(self, populated_map):
        """remove() deve retornar o valor associado à chave removida."""
        val = populated_map.remove("city")
        assert val == "São Paulo"

    def test_remove_decrements_size(self, populated_map):
        """size() deve diminuir após remoção."""
        before = populated_map.size()
        populated_map.remove("score")
        assert populated_map.size() == before - 1

    def test_removed_key_not_found(self, populated_map):
        """Chave removida não deve mais ser encontrada."""
        populated_map.remove("active")
        assert populated_map.get("active") is None


# ---------------------------------------------------------------------------
# Cenário 4 – Verificação de existência
# ---------------------------------------------------------------------------

class TestContains:
    def test_contains_existing_key(self, populated_map):
        assert populated_map.contains("name") is True

    def test_contains_missing_key(self, populated_map):
        assert populated_map.contains("missing") is False

    def test_in_operator(self, populated_map):
        """Operador `in` deve funcionar via __contains__."""
        assert "age" in populated_map


# ---------------------------------------------------------------------------
# Cenário 5 – Tamanho e estado vazio
# ---------------------------------------------------------------------------

class TestSizeAndEmpty:
    def test_empty_map_size_is_zero(self, empty_map):
        assert empty_map.size() == 0

    def test_is_empty_on_new_map(self, empty_map):
        assert empty_map.is_empty() is True

    def test_is_not_empty_after_insert(self, empty_map):
        empty_map.put("k", "v")
        assert empty_map.is_empty() is False

    def test_size_after_multiple_inserts(self, empty_map):
        for i in range(10):
            empty_map.put(i, i * 2)
        assert empty_map.size() == 10


# ---------------------------------------------------------------------------
# Cenário 6 – Limpeza
# ---------------------------------------------------------------------------

class TestClear:
    def test_clear_empties_map(self, populated_map):
        populated_map.clear()
        assert populated_map.size() == 0
        assert populated_map.is_empty() is True

    def test_can_insert_after_clear(self, populated_map):
        populated_map.clear()
        populated_map.put("new", "value")
        assert populated_map.get("new") == "value"


# ---------------------------------------------------------------------------
# Cenário 7 – Iteração e listagem
# ---------------------------------------------------------------------------

class TestIterationAndListing:
    def test_keys_returns_all_keys(self, populated_map):
        keys = populated_map.keys()
        assert set(keys) == {"name", "age", "city", "score", "active"}

    def test_values_returns_all_values(self, populated_map):
        values = populated_map.values()
        assert set(values) == {"Alice", 30, "São Paulo", 9.5, True}

    def test_items_returns_pairs(self, populated_map):
        items = dict(populated_map.items())
        assert items["name"] == "Alice"
        assert items["age"] == 30

    def test_iter_yields_all_keys(self, populated_map):
        keys_via_iter = list(populated_map)
        assert set(keys_via_iter) == set(populated_map.keys())


# ---------------------------------------------------------------------------
# Cenário 8 – Sintaxe de dicionário (operadores Python)
# ---------------------------------------------------------------------------

class TestDictSyntax:
    def test_setitem_and_getitem(self, empty_map):
        empty_map["x"] = 10
        assert empty_map["x"] == 10

    def test_delitem(self, populated_map):
        del populated_map["name"]
        assert "name" not in populated_map

    def test_len_operator(self, populated_map):
        assert len(populated_map) == 5


# ---------------------------------------------------------------------------
# Cenário 9 – Rehashing automático
# ---------------------------------------------------------------------------

class TestRehashing:
    def test_rehash_preserves_all_entries(self):
        """Após rehash, todos os pares devem continuar acessíveis."""
        hm = HashMap(capacity=4)
        for i in range(20):          # força múltiplos rehashes
            hm.put(f"key{i}", i)
        for i in range(20):
            assert hm.get(f"key{i}") == i

    def test_capacity_grows_after_threshold(self):
        hm = HashMap(capacity=4)
        for i in range(10):
            hm.put(i, i)
        assert hm.capacity() > 4


# ---------------------------------------------------------------------------
# Cenário 10 – Tipos de valor variados
# ---------------------------------------------------------------------------

class TestVariousValueTypes:
    def test_none_as_value(self, empty_map):
        empty_map.put("null_val", None)
        assert empty_map.get("null_val") is None
        assert empty_map.contains("null_val") is True

    def test_list_as_value(self, empty_map):
        empty_map.put("lista", [1, 2, 3])
        assert empty_map.get("lista") == [1, 2, 3]

    def test_nested_map_as_value(self, empty_map):
        inner = HashMap()
        inner.put("a", 1)
        empty_map.put("nested", inner)
        assert empty_map.get("nested").get("a") == 1

    def test_zero_and_false_as_values(self, empty_map):
        """Valores falsy (0, False) devem ser armazenados corretamente."""
        empty_map.put("zero", 0)
        empty_map.put("false", False)
        assert empty_map.get("zero") == 0
        assert empty_map.get("false") is False


# ---------------------------------------------------------------------------
# Cenário 11 – Representação e igualdade
# ---------------------------------------------------------------------------

class TestReprAndEquality:
    def test_repr_contains_key(self, populated_map):
        assert "name" in repr(populated_map)

    def test_two_maps_with_same_content_are_equal(self):
        a, b = HashMap(), HashMap()
        a.put("x", 1)
        b.put("x", 1)
        assert a == b

    def test_maps_with_different_content_are_not_equal(self, populated_map, empty_map):
        assert populated_map != empty_map