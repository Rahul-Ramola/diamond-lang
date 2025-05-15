# lexer.py

def tokenize(code):
    tokens = []
    lines = code.splitlines()
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith("#"):
            continue

        # Print statement: sun dost
        if line.startswith("sun dost"):
            tokens.append(("PRINT", line[8:].strip()))
        
        # Variable declaration: mera dost
        elif line.startswith("mera dost"):
            var_part = line[9:].strip()
            if "=" in var_part:
                var_name, value = var_part.split("=", 1)
                tokens.append(("VAR_DECLARATION", var_name.strip(), value.strip()))
            else:
                tokens.append(("VAR_DECLARATION", var_part.strip(), None))
        
        # Function definition: kaam dost
        elif line.startswith("kaam dost"):
            func_def = line[9:].strip()
            if "(" in func_def and ")" in func_def:
                # Extract function name and parameters
                func_name = func_def[:func_def.find("(")].strip()
                params_str = func_def[func_def.find("(")+1:func_def.find(")")].strip()
                params = [p.strip() for p in params_str.split(",")] if params_str else []
                tokens.append(("FUNC_DEF", func_name, params))
            else:
                tokens.append(("FUNC_DEF", func_def, []))
        
        # Function call: bula dost
        elif line.startswith("bula dost"):
            func_call = line[9:].strip()
            if "(" in func_call and ")" in func_call:
                # Extract function name and arguments
                func_name = func_call[:func_call.find("(")].strip()
                args_str = func_call[func_call.find("(")+1:func_call.find(")")].strip()
                args = [arg.strip() for arg in args_str.split(",")] if args_str else []
                tokens.append(("FUNC_CALL", func_name, args))
            else:
                tokens.append(("FUNC_CALL", func_call.replace("()", ""), []))
        
        # Return statement: wapas dost
        elif line.startswith("wapas dost"):
            value = line[10:].strip()
            tokens.append(("RETURN", value if value else None))
        
        # If statement: agar dost
        elif line.startswith("agar dost"):
            condition = line[9:].strip()
            tokens.append(("IF", condition))
        
        # Else statement: warna dost
        elif line.startswith("warna dost"):
            tokens.append(("ELSE", None))
        
        # While loop: jab tak dost
        elif line.startswith("jab tak dost"):
            condition = line[12:].strip()
            tokens.append(("WHILE", condition))
        
        # For loop: ghum dost
        elif line.startswith("ghum dost"):
            parts = line[9:].strip().split()
            if len(parts) >= 5 and parts[1] == "se" and "tak" in line:
                var_name = parts[0]
                start = parts[2]
                end = parts[4]
                step = parts[6] if len(parts) > 6 else "1"
                tokens.append(("FOR", var_name, start, end, step))
        
        # End of block: bas dost
        elif line.startswith("bas dost"):
            tokens.append(("END", None))
        
        # Unknown token
        else:
            tokens.append(("UNKNOWN", line))
    
    return tokens
