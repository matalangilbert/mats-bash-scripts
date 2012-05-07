#!/bin/bash
aspell --mode=tex --add-tex-command="citep p" --add-tex-command="bibliographystyle p" check $1
