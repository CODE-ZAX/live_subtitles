import React from "react";
import { Video, Sparkles } from "lucide-react";

const Header = () => {
  return (
    <header className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
              <Video className="h-8 w-8 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gradient">
                AI Video Transcription Studio
              </h1>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Transform your videos with AI-powered subtitles
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
            <Sparkles className="h-4 w-4" />
            <span>Made to outshine</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
