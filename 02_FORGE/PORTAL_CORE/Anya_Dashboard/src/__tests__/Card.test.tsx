import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card } from '../components/ui/Card';

describe('Card Component', () => {
  it('renders title and description correctly', () => {
    render(<Card title="Test Title" description="Test Description" />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
  });

  it('renders children content', () => {
    render(
      <Card>
        <div>Child Content</div>
      </Card>,
    );
    expect(screen.getByText('Child Content')).toBeInTheDocument();
  });

  it('renders actions in the header', () => {
    render(<Card title="Header" actions={<button>Action</button>} />);
    expect(screen.getByRole('button', { name: 'Action' })).toBeInTheDocument();
  });

  it('renders footer content', () => {
    render(<Card footer={<span>Footer Content</span>} />);
    expect(screen.getByText('Footer Content')).toBeInTheDocument();
  });
});
