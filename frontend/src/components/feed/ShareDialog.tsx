import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Copy, Code, Mail, Check } from "lucide-react";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

type ShareDialogProps = {
  isOpen: boolean;
  onClose: () => void;
  articleUrl: string;
  articleTitle: string;
};

export const ShareDialog = ({ isOpen, onClose, articleUrl, articleTitle }: ShareDialogProps) => {
  const { toast } = useToast();
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(articleUrl);
      setCopied(true);
      toast({ title: "Link copied to clipboard" });
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast({ title: "Failed to copy link", variant: "destructive" });
    }
  };

  const shareLinks = [
    {
      name: "Embed",
      icon: <Code className="h-5 w-5" />,
      color: "bg-gray-100 hover:bg-gray-200 text-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700 dark:text-gray-300",
      action: () => {
        // For now just copy embed code or show a toast
        toast({ title: "Embed code copied (simulated)" });
      }
    },
    {
      name: "WhatsApp",
      icon: (
        <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current" xmlns="http://www.w3.org/2000/svg">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
      ),
      color: "bg-green-500 hover:bg-green-600 text-white",
      action: () => window.open(`https://wa.me/?text=${encodeURIComponent(articleTitle + " " + articleUrl)}`, "_blank")
    },
    {
      name: "Facebook",
      icon: (
        <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current" xmlns="http://www.w3.org/2000/svg">
          <path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036c-2.148 0-2.797 1.603-2.797 2.87v1.12h5.306l-1.008 3.667h-4.298v7.98c0 .003-.001.005-.001.008h-5.016c0-.003-.001-.005-.001-.008Z"/>
        </svg>
      ),
      color: "bg-blue-600 hover:bg-blue-700 text-white",
      action: () => window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(articleUrl)}`, "_blank")
    },
    {
      name: "X",
      icon: (
        <svg viewBox="0 0 24 24" className="h-4 w-4 fill-current" xmlns="http://www.w3.org/2000/svg">
          <path d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/>
        </svg>
      ),
      color: "bg-black hover:bg-gray-900 text-white dark:bg-white dark:hover:bg-gray-100 dark:text-black",
      action: () => window.open(`https://twitter.com/intent/tweet?text=${encodeURIComponent(articleTitle)}&url=${encodeURIComponent(articleUrl)}`, "_blank")
    },
    {
      name: "Email",
      icon: <Mail className="h-5 w-5" />,
      color: "bg-gray-500 hover:bg-gray-600 text-white",
      action: () => window.open(`mailto:?subject=${encodeURIComponent(articleTitle)}&body=${encodeURIComponent(articleUrl)}`, "_blank")
    }
  ];

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Share in a post</DialogTitle>
        </DialogHeader>
        
        <div className="flex flex-col gap-6 py-4">
          <div className="flex justify-center">
            <Button className="rounded-full px-8">
              Create post
            </Button>
          </div>
          
          <div className="text-center text-sm text-muted-foreground">
            No subscribers
          </div>

          <div className="space-y-4">
            <h4 className="text-sm font-medium leading-none">Share</h4>
            <div className="flex items-center justify-center gap-4">
              {shareLinks.map((link) => (
                <div key={link.name} className="flex flex-col items-center gap-2">
                  <button
                    onClick={link.action}
                    className={`h-12 w-12 rounded-full flex items-center justify-center transition-transform hover:scale-110 ${link.color}`}
                    title={link.name}
                  >
                    {link.icon}
                  </button>
                  <span className="text-xs text-muted-foreground">{link.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <div className="grid flex-1 gap-2">
              <Input
                readOnly
                value={articleUrl}
                className="h-9"
              />
            </div>
            <Button size="sm" onClick={handleCopy} className="px-3">
              {copied ? (
                <Check className="h-4 w-4" />
              ) : (
                <span className="sr-only">Copy</span>
              )}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
