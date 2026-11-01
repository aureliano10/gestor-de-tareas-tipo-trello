import { Component } from "react";

/** Barrera de errores: evita que una excepción de render deje la app en blanco. */
export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // Se deja en consola para el diagnóstico, sin exponerlo en la interfaz.
    console.error("Error inesperado en la interfaz:", error, info);
  }

  render() {
    if (this.state.error) {
      return (
        <main className="app">
          <div className="alert" role="alert" data-testid="app-crash">
            Ocurrió un error inesperado. Recargá la página para continuar.
          </div>
        </main>
      );
    }
    return this.props.children;
  }
}
