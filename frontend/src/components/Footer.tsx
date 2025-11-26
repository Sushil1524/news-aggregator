import { Newspaper } from "lucide-react";
import { Link } from "react-router-dom";

export const Footer = () => {
  return (
    <footer className="border-t border-border bg-card">
      <div className="container py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <Link to="/" className="flex items-center gap-2 font-bold text-xl mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-primary">
                <Newspaper className="h-5 w-5 text-primary-foreground" />
              </div>
              <span>IntelliNews</span>
            </Link>
            <p className="text-sm text-muted-foreground max-w-md">
              An intelligent news aggregator designed for finance and market enthusiasts. 
              Stay informed and learn smarter with AI-powered tools.
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Product</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/feed" className="hover:text-foreground transition-colors">
                  News Feed
                </Link>
              </li>
              <li>
                <Link to="/finance" className="hover:text-foreground transition-colors">
                  Finance
                </Link>
              </li>
              <li>
                <Link to="/study-tools" className="hover:text-foreground transition-colors">
                  Study Tools
                </Link>
              </li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Company</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/about" className="hover:text-foreground transition-colors">
                  About
                </Link>
              </li>
              <li>
                <Link to="/contact" className="hover:text-foreground transition-colors">
                  Contact
                </Link>
              </li>
              <li>
                <Link to="/privacy" className="hover:text-foreground transition-colors">
                  Privacy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-border text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} IntelliNews.</p>
        </div>
      </div>
    </footer>
  );
};
