import { render, screen } from '@testing-library/react';
import App from './App';

test('renders chat component', () => {
  render(<App />);
  const chatElement = screen.getByTestId('chat');
  expect(chatElement).toBeInTheDocument();
});
