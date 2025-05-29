# Anthropic Prompt Engineering Guide

> A comprehensive guide for maximizing LLM output quality based on Anthropic's principles and best practices

## Core Principles

### 1. Foundation Before Engineering

- Define clear success criteria before starting
- Establish empirical evaluation methods
- Create initial prompt drafts for iteration
- Ensure you understand the task requirements fully

### 2. When to Use Prompt Engineering

- For rapid iteration needs
- When resource efficiency is important
- When flexibility in domain adaptation is required
- When transparency in debugging is needed

### 3. General Best Practices

#### Be Clear and Direct

- Use specific, unambiguous instructions
- State exactly what you want, not what to avoid
- Include context and motivation for requirements
- Break complex tasks into smaller, manageable steps

#### Structure and Format

- Use XML tags to separate different parts of prompts
- Mirror desired output format in the prompt
- Employ consistent formatting across related prompts
- Use clear section headers and organization

#### Context and Examples

- Provide relevant context upfront
- Include examples of desired output format
- Use multishot prompting for complex tasks
- Show both correct and incorrect examples when relevant

### 4. Advanced Techniques

#### Chain-of-Thought Prompting

- Encourage step-by-step reasoning
- Use "think" instructions for complex problems
- Allow the model to break down complex tasks
- Request explanations for decisions

#### Role and Context Setting

- Assign specific roles when needed
- Provide relevant background information
- Set clear boundaries and constraints
- Define the scope of the interaction

#### Output Control

- Specify exact output formats
- Use templates for consistent responses
- Include validation criteria
- Define error handling expectations

### 5. Claude 4-Specific Optimizations

#### Enhanced Instructions

- Be explicit about requirements
- Add detailed context and motivation
- Request comprehensive feature inclusion
- Use modifiers to enhance detail

#### Parallel Processing

- Leverage simultaneous tool calling
- Enable parallel task execution
- Utilize thinking capabilities
- Optimize for complex workflows

### 6. Working with Code

#### Agentic Coding Best Practices

- Use CLAUDE.md files for environment documentation
- Implement tool allowlisting for safety
- Follow explore-plan-code-commit workflow
- Leverage test-driven development approaches

#### Multi-Instance Workflows

- Run parallel work sessions
- Separate concerns across instances
- Enable concurrent task processing
- Maintain clear role separation

### 7. Information Extraction and RAG

#### Context Management

- Isolate different types of context
- Use clear delineation between sections
- Maintain context relevance
- Implement efficient retrieval strategies

#### Quality Control

- Allow uncertainty acknowledgment
- Implement fact-checking mechanisms
- Use structured output formats
- Validate against source material

## Implementation Guidelines

### 1. Prompt Structure Template

```
<context>
[Relevant background information]
</context>

<task>
[Specific instructions and requirements]
</task>

<format>
[Expected output format and structure]
</format>

<examples>
[Sample inputs and outputs]
</examples>

<constraints>
[Any limitations or requirements]
</constraints>
```

### 2. Quality Checklist

- [ ] Clear success criteria defined
- [ ] Specific instructions provided
- [ ] Relevant context included
- [ ] Output format specified
- [ ] Examples provided when needed
- [ ] Constraints clearly stated
- [ ] Error handling addressed
- [ ] Validation criteria included

### 3. Common Pitfalls to Avoid

1. Vague or ambiguous instructions
2. Insufficient context
3. Unclear output requirements
4. Missing validation criteria
5. Overcomplicated prompts
6. Insufficient examples
7. Unclear error handling
8. Poor structure and organization

### 4. Optimization Process

1. Start with basic prompt
2. Test with sample inputs
3. Analyze outputs
4. Identify improvement areas
5. Refine instructions
6. Add relevant context
7. Enhance structure
8. Validate results
9. Iterate as needed

## Best Practices Summary

1. **Clarity First**

   - Be explicit and direct
   - Avoid ambiguity
   - State requirements clearly
   - Provide necessary context

2. **Structure Matters**

   - Use consistent formatting
   - Implement clear organization
   - Separate different components
   - Maintain logical flow

3. **Context is Key**

   - Include relevant background
   - Provide necessary examples
   - Set clear boundaries
   - Define scope properly

4. **Validation Important**

   - Define success criteria
   - Include error handling
   - Specify output requirements
   - Implement quality checks

5. **Iterative Improvement**
   - Start simple
   - Test thoroughly
   - Refine based on results
   - Optimize incrementally

## Conclusion

Effective prompt engineering with Anthropic's models requires a systematic approach combining clear instructions, proper structure, relevant context, and continuous refinement. By following these guidelines and best practices, you can maximize the quality and reliability of LLM outputs while maintaining efficiency and effectiveness in your applications.

Remember that prompt engineering is an iterative process, and what works best may vary depending on your specific use case. Regular testing and refinement of prompts based on actual results will help achieve optimal performance.
