# Task Completion Checklist

## Before Committing Code

### 1. Syntax Validation
Run Python syntax check:
```bash
python3 -m py_compile app.py
python3 -m py_compile database/bigquery_client.py
python3 -m py_compile utils/data_processing.py
```

### 2. Test the Application
```bash
streamlit run app.py
```
Verify:
- Application starts without errors
- All new features work as expected
- Existing features still work (no regressions)
- Filters cascade properly
- Data loads correctly

### 3. Code Quality Checks
- [ ] No hardcoded credentials or sensitive data
- [ ] All functions use appropriate caching (`@st.cache_data` or `@st.cache_resource`)
- [ ] Error handling for BigQuery queries
- [ ] Loading states for long operations
- [ ] Responsive design (check on different screen sizes)
- [ ] Column existence checks before processing
- [ ] Empty DataFrame checks

### 4. Documentation
- [ ] Update CLAUDE.md if architecture changes
- [ ] Add inline comments for complex logic
- [ ] Update README.md if user-facing features change

## No Formal Linting/Formatting
The project does not currently use formal linting tools (pylint, flake8, black). Manual code review is sufficient.