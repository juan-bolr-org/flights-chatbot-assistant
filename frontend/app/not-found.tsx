export default function NotFound() {
  return (
    <main className="flex flex-col items-center justify-center min-h-[60vh]">
      <h1 className="next-error-h1">404</h1>
      <p className="text-lg text-gray-600 mb-6">La página que buscas no existe.</p>
      <a
        href="/"
        className="btn btn-primary"
      >
        Polvora
      </a>
    </main>
  );
}