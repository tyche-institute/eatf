# Contributing to Aletheia AI

Thank you for your interest in contributing to the Enterprise Agent Trust Framework!

---

## 🚀 Quick Start for Contributors

**This repository is private.** A curated subset of the source is
mirrored to the public [`tyche-institute`](https://github.com/tyche-institute)
GitHub organization (specs, public SDKs, top-level legal/security
docs). Before adding or moving material you expect to be visible
publicly, see [`docs/legal/public-mirror-policy.md`](./docs/legal/public-mirror-policy.md)
and [`.public-mirror/manifest.yml`](./.public-mirror/manifest.yml).

If you're a collaborator:

1. **Clone the repository**
   ```bash
   git clone https://github.com/anton/aletheia-ai.git
   cd aletheia-ai
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make changes, commit, push**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** (see `CODEOWNERS` for required reviewers)

5. **Wait for review** — All PRs require approval before merge

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Code Style Guidelines](#code-style-guidelines)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation Guidelines](#documentation-guidelines)

---

## 📜 Code of Conduct

Be respectful, professional, and constructive. We're building trust infrastructure — let's model trustworthy collaboration.

---

## 🤝 How Can I Contribute?

### Reporting Bugs
- Check existing issues first
- Use issue templates
- Include reproduction steps
- Attach logs, screenshots if relevant

### Suggesting Features
- Describe the use case
- Explain why it's valuable
- Consider security implications (this is a trust framework!)

### Submitting Code
- Fork the repository
- Create a feature branch
- Write tests for new functionality
- Ensure all tests pass
- Submit a pull request

### Improving Documentation
- Fix typos, clarify ambiguities
- Add examples
- Update outdated content
- Translate docs (RU, ET)

---

## 🛠️ Development Setup

### Prerequisites
- **Backend:** Java 21, Maven 3.8+
- **Frontend:** Node.js 18+, npm 9+
- **Database:** PostgreSQL 14+ (dev mode uses H2)
- **Git:** For version control

### Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/aletheia-ai.git
cd aletheia-ai

# Backend setup
cd backend
mvn clean install
mvn spring-boot:run

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

**Full setup guide:** [docs/developers/en/quickstart.md](docs/developers/en/quickstart.md)

---

## 🎨 Code Style Guidelines

### Java (Backend)

- **Style:** Follow [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- **Formatting:** Use IntelliJ default formatter
- **Naming:**
  - Classes: `PascalCase`
  - Methods: `camelCase`
  - Constants: `UPPER_SNAKE_CASE`
- **Comments:**
  - Javadoc for public APIs
  - Inline comments for complex logic
  - No commented-out code in PRs

**Example:**
```java
/**
 * Generates cryptographic attestation for AI agent response.
 *
 * @param response The AI response to attest
 * @param agentId The agent identifier
 * @return Signed evidence package with timestamp
 * @throws SigningException if signature generation fails
 */
public EvidencePackage attestResponse(AgentResponse response, String agentId) {
    // Validate inputs
    validateResponse(response);
    validateAgentId(agentId);
    
    // Generate canonical representation
    byte[] canonical = canonicalizer.serialize(response);
    
    // Sign with PQC keys
    return signer.signWithTimestamp(canonical, agentId);
}
```

### TypeScript/React (Frontend)

- **Style:** Prettier + ESLint (configs in repo)
- **Components:** Functional components with hooks
- **Types:** Always use TypeScript types, avoid `any`
- **Naming:**
  - Components: `PascalCase`
  - Functions: `camelCase`
  - Files: `kebab-case.tsx`
- **Imports:** Organize (React → 3rd-party → local)

**Example:**
```typescript
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { fetchAgentDetails } from '@/lib/api';

interface AgentCardProps {
  agentId: string;
  onSelect: (agentId: string) => void;
}

export function AgentCard({ agentId, onSelect }: AgentCardProps) {
  const [agent, setAgent] = useState<Agent | null>(null);
  
  useEffect(() => {
    fetchAgentDetails(agentId).then(setAgent);
  }, [agentId]);
  
  if (!agent) return <LoadingSpinner />;
  
  return (
    <div className="agent-card">
      <h3>{agent.name}</h3>
      <Button onClick={() => onSelect(agentId)}>
        Select Agent
      </Button>
    </div>
  );
}
```

---

## 📝 Commit Message Guidelines

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Build, dependencies, tooling

### Examples:

```
feat(agents): Add delegation chain validation

Implement multi-level delegation chain validation with policy
enforcement. Supports up to 5 delegation levels.

Closes #123
```

```
fix(audit): Correct timestamp parsing in audit trail

Fixed RFC 3161 timestamp parsing that failed for some TSA responses.

Fixes #456
```

```
docs(api): Update API reference with new endpoints

Added documentation for /api/v1/delegation-chains and
/api/v1/audit/events endpoints.
```

### Rules:
- Use present tense ("add" not "added")
- Use imperative mood ("move" not "moves")
- First line ≤ 72 characters
- Reference issues/PRs when applicable

---

## 🔄 Pull Request Process

### Before Submitting

1. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

2. **Write tests:**
   - Unit tests for business logic
   - Integration tests for API endpoints
   - E2E tests for critical user flows

3. **Run tests locally:**
   ```bash
   # Backend
   cd backend && mvn test
   
   # Frontend
   cd frontend && npm test
   ```

4. **Update documentation:**
   - Update relevant docs in `/docs`
   - Add API documentation if adding endpoints
   - Update README if changing setup

5. **Lint and format:**
   ```bash
   # Backend (IntelliJ formatter)
   # Frontend
   cd frontend && npm run lint && npm run format
   ```

### Submitting PR

1. **Push to your fork:**
   ```bash
   git push origin feat/your-feature-name
   ```

2. **Open PR on GitHub:**
   - Use descriptive title
   - Fill out PR template
   - Link related issues
   - Add screenshots for UI changes
   - Request review from maintainers

3. **Respond to feedback:**
   - Address review comments
   - Push additional commits
   - Re-request review when ready

### PR Checklist

- [ ] Tests added/updated and passing
- [ ] Documentation updated
- [ ] Code follows style guidelines
- [ ] Commit messages follow conventions
- [ ] No merge conflicts
- [ ] PR description is clear
- [ ] Related issues linked

---

## 📚 Documentation Guidelines

### Structure

- **Filename:** `lowercase-with-hyphens.md`
- **Location:**
  - User docs → `docs/users/en/`
  - Developer docs → `docs/developers/en/`
  - Internal docs → `docs/internal/en/`
  - API docs → `docs/api/`

### Format

```markdown
# Document Title

Brief description (1-2 sentences).

---

## Section 1

Content here...

### Subsection 1.1

More specific content...

## Section 2

...

---

## Related Documents

- [Related Doc 1](./related-doc-1.md)
- [Related Doc 2](./related-doc-2.md)
```

### Best Practices

1. **Be concise** — Remove unnecessary words
2. **Use examples** — Show, don't just tell
3. **Code samples** — Always include working code
4. **Screenshots** — For UI features
5. **Keep updated** — Update docs with code changes
6. **Link liberally** — Connect related documents
7. **Test instructions** — Verify docs work as written

### Markdown Style

- Use ATX headers (`#` not `===`)
- Use fenced code blocks with language:
  ````markdown
  ```java
  public class Example {}
  ```
  ````
- Use tables for structured data
- Use lists for enumerations
- Link to other docs with relative paths

---

## 🔐 Security

### Reporting Vulnerabilities

**DO NOT** open public issues for security vulnerabilities!

Instead:
1. Email: security@aletheia.ai
2. Provide details: steps to reproduce, impact assessment
3. Wait for response (we aim for 48h)

### Security Best Practices

- Never commit secrets, keys, or credentials
- Use environment variables for sensitive config
- Follow OWASP guidelines
- Validate all inputs
- Use parameterized queries (SQL injection)
- Implement rate limiting
- Log security events

---

## 🧪 Testing Guidelines

### Test Types

1. **Unit Tests** — Test individual functions/classes
2. **Integration Tests** — Test API endpoints, database interactions
3. **E2E Tests** — Test critical user flows

### Coverage Goals

- **Backend:** ≥80% line coverage
- **Frontend:** ≥70% line coverage
- **Critical paths:** 100% coverage (auth, crypto, audit)

### Writing Good Tests

```java
@Test
void shouldRejectDelegationWithExpiredChain() {
    // Given
    Agent agent = createTestAgent();
    DelegationChain chain = createExpiredChain();
    
    // When & Then
    assertThrows(DelegationException.class, () -> {
        delegationService.validateChain(agent, chain);
    });
}
```

**Principles:**
- One assertion per test (when possible)
- Descriptive test names (`shouldRejectInvalidInput` not `test1`)
- Use Given-When-Then structure
- Mock external dependencies
- Test edge cases and error paths

---

## 🎯 Review Process

### For Reviewers

- **Be constructive** — Suggest improvements, don't just criticize
- **Be timely** — Review within 2 business days
- **Be thorough** — Check code, tests, docs
- **Ask questions** — Seek clarification on unclear changes

### For Contributors

- **Be responsive** — Address feedback promptly
- **Be open** — Consider alternative approaches
- **Be patient** — Quality takes time

---

## 📞 Getting Help

- **Documentation:** [docs/README.md](docs/README.md)
- **GitHub Discussions:** Ask questions, share ideas
- **GitHub Issues:** Bug reports, feature requests
- **Email:** dev@aletheia.ai

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Aletheia AI better! 🙏**
