# Verification Guide: embedding-generator

This guide helps verify the embedding-generator module implementation.

## Quick Verification Steps

### Step 1: Module Structure Verification

Check that all required files exist:

```bash
cd /Users/source-code/vertex-ai-search/worktrees/feature-4/embedding-generator/

# Verify structure
ls -la
# Expected: Makefile, pyproject.toml, README.md, CLAUDE.md, src/, tests/

ls -la src/embedding_generator/
# Expected: __init__.py, generator.py

ls -la tests/
# Expected: __init__.py, test_generator.py
```

### Step 2: Dependency Installation

```bash
# Install dependencies
make setup

# Verify Poetry environment
poetry env info

# List installed packages
poetry show
```

### Step 3: Run Tests (GREEN Phase Verification)

```bash
# Run all tests with verbose output
make test

# Expected output:
# - 6 test cases pass
# - test_generate_single_embedding ✓
# - test_generate_batch_embeddings ✓
# - test_generate_with_batch_processing ✓
# - test_generate_with_retry_on_failure ✓
# - test_generate_empty_list ✓
# - test_initialization_defaults ✓
```

### Step 4: Coverage Verification

```bash
# Run tests with coverage report
make test-cov

# Expected output:
# - Coverage: 80%+ (minimum requirement)
# - HTML report in htmlcov/index.html
```

### Step 5: Code Quality Checks (REFACTOR Phase)

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck

# All quality checks
make quality
```

### Step 6: Build Verification

```bash
# Build package
make build

# Expected output:
# - Wheel file in dist/
# - embedding_generator-0.1.0-py3-none-any.whl
```

### Step 7: Independence Verification

```bash
# Clean and rebuild from scratch
make clean
make setup
make test
make build

# All steps should succeed without errors
```

## Detailed Test Verification

### Test 1: Single Embedding Generation

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_single_embedding -v
```

**Expected Behavior**:
- Creates single TextChunk
- Mocks Vertex AI API response
- Generates single Vector768 with 768 dimensions
- Verifies chunk_id mapping
- Verifies model name

### Test 2: Batch Embeddings

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_batch_embeddings -v
```

**Expected Behavior**:
- Creates 3 TextChunks
- Mocks multiple API responses
- Generates 3 Vector768 objects
- Verifies all chunk_ids mapped correctly

### Test 3: Batch Processing

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_with_batch_processing -v
```

**Expected Behavior**:
- Creates 5 TextChunks
- Sets batch_size=2
- Verifies API called multiple times (3 batches: 2+2+1)
- All 5 vectors generated correctly

### Test 4: Retry Logic

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_with_retry_on_failure -v
```

**Expected Behavior**:
- First API call fails with Exception
- Second API call succeeds
- Verifies retry was attempted
- Verifies exponential backoff (time.sleep called)

### Test 5: Empty List

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_generate_empty_list -v
```

**Expected Behavior**:
- Input: empty list []
- Output: empty list []
- No API calls made

### Test 6: Initialization Defaults

```bash
poetry run pytest tests/test_generator.py::TestEmbeddingGenerator::test_initialization_defaults -v
```

**Expected Behavior**:
- Verifies vertexai.init called with project and location
- Verifies batch_size defaults to 100
- Verifies max_retries defaults to 3

## Coverage Report Analysis

After running `make test-cov`, open the HTML report:

```bash
# Open coverage report in browser
open htmlcov/index.html
```

**Expected Coverage**:
- `src/embedding_generator/__init__.py`: 100%
- `src/embedding_generator/generator.py`: 85%+ (minimum)
- **Total**: 80%+ (required)

**Uncovered Lines** (acceptable):
- Error handling edge cases
- Unreachable return statements (type checker satisfaction)

## Code Quality Verification

### Black Formatting

```bash
poetry run black --check src/ tests/

# Expected: All files formatted correctly (88 char line length)
```

### Ruff Linting

```bash
poetry run ruff check src/ tests/

# Expected: No linting errors
```

### Mypy Type Checking

```bash
poetry run mypy src/

# Expected: No type errors (strict mode)
```

## Manual Code Review Checklist

- [ ] All functions have type annotations
- [ ] All imports are used
- [ ] No commented-out code
- [ ] Docstrings are clear and accurate
- [ ] No print() statements for debugging
- [ ] Exception handling is appropriate
- [ ] Variable names are descriptive
- [ ] Code follows PEP 8 style guide
- [ ] No magic numbers (batch_size, max_retries are configurable)
- [ ] No unnecessary complexity

## Integration Verification

### Import Test

```bash
poetry run python -c "
from embedding_generator import EmbeddingGenerator
from shared_contracts import TextChunk, Vector768
print('Imports successful')
"
```

### Type Validation Test

```bash
poetry run python -c "
from embedding_generator import EmbeddingGenerator
from shared_contracts import TextChunk, Vector768

chunk = TextChunk(
    chunk_id='test-1',
    content='Test content',
    metadata={},
    token_count=5,
    source_file='test.html'
)
print(f'TextChunk created: {chunk.chunk_id}')

# This would require actual Vertex AI credentials
# generator = EmbeddingGenerator(project_id='test', location='us-central1')
print('Type validation successful')
"
```

## Performance Considerations

### Batch Size Impact

The default batch size (100) balances:
- **API efficiency**: Fewer API calls
- **Memory usage**: Reasonable memory footprint
- **Rate limits**: Respects Vertex AI quotas

### Retry Logic Impact

The exponential backoff (2^attempt):
- Attempt 1: 1 second wait
- Attempt 2: 2 seconds wait
- Attempt 3: 4 seconds wait (if needed)

Total max wait time: ~7 seconds for 3 retries

## Common Issues and Solutions

### Issue: Tests fail with import errors

**Solution**:
```bash
make clean
make setup
poetry install
```

### Issue: Coverage below 80%

**Solution**:
- Review untested code paths
- Add edge case tests
- Ensure all branches are covered

### Issue: Type checking fails

**Solution**:
- Verify all functions have type annotations
- Check return types match declarations
- Run `poetry run mypy src/ --show-error-codes`

### Issue: Linting errors

**Solution**:
```bash
make format  # Auto-fix most issues
make lint    # Check remaining issues
```

## Success Criteria Checklist

- [ ] Module structure follows Pure Module Isolation
- [ ] All 6 tests pass
- [ ] Coverage >= 80%
- [ ] Black formatting passes
- [ ] Ruff linting passes
- [ ] Mypy type checking passes
- [ ] Independent build succeeds
- [ ] Module has <60 files
- [ ] Documentation is complete
- [ ] Ready for integration

## Next Steps After Verification

1. **Commit changes**: Follow Git commit conventions
2. **Create pull request**: Link to issue #4
3. **Request code review**: Share verification results
4. **Integration testing**: Test with chunker and indexer modules
5. **Performance testing**: Verify batch processing efficiency
6. **Documentation update**: Add to main project README

## Support

For issues or questions:
1. Check CLAUDE.md for module-specific guidance
2. Review test cases for usage examples
3. Check TDD_IMPLEMENTATION_SUMMARY.md for implementation details
4. Review shared-contracts documentation for data models
