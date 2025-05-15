from lexer import tokenize

# Store functions and their scopes
functions = {}
# Store the current loop context
loop_context = {
    'break': False,
    'continue': False,
    'return_value': None
}

current_scope = None

class Scope:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent
        self.return_value = None

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return globals().get(name)

    def set(self, name, value):
        self.variables[name] = value

def evaluate_expression(expr, scope):
    if isinstance(expr, str):
        if expr.startswith("bula dost"):
            # Handle function calls
            func_call = expr.strip()
            func_name = func_call[9:func_call.find("(")].strip()
            args_str = func_call[func_call.find("(")+1:func_call.find(")")].strip()
            args = [arg.strip() for arg in args_str.split(",")] if args_str else []
            result = execute_token(("FUNC_CALL", func_name, args))
            return result if result is not None else expr
        try:
            return eval(expr, globals(), scope.variables if scope else None)
        except:
            return expr
    return expr

def execute_token(token, tokens=None, index=None):
    global current_scope, functions
    
    if token[0] == "PRINT":
        try:
            # Handle string concatenation with variables
            if "+" in token[1] and ('"' in token[1] or "'" in token[1]):
                parts = token[1].split("+")
                result = ""
                for part in parts:
                    part = part.strip()
                    if part.startswith('"') and part.endswith('"'):
                        result += part[1:-1]
                    elif part.startswith("'") and part.endswith("'"):
                        result += part[1:-1]
                    else:
                        val = evaluate_expression(part, current_scope)
                        result += str(val)
                print(result)
            else:
                value = evaluate_expression(token[1], current_scope)
                print(value)
        except Exception as e:
            print(f"Error in print: {e}")
            print(token[1])
    
    elif token[0] == "VAR_DECLARATION":
        var_name = token[1]
        if token[2] is not None:
            value = evaluate_expression(token[2], current_scope)
            if current_scope:
                current_scope.set(var_name, value)
            else:
                globals()[var_name] = value
        else:
            if current_scope:
                current_scope.set(var_name, None)
            else:
                globals()[var_name] = None

    elif token[0] == "FUNC_DEF":
        func_name = token[1]
        params = token[2]
        
        # Collect function body until END
        if tokens and index:
            body = []
            i = index + 1
            while i < len(tokens) and tokens[i][0] != "END":
                body.append(tokens[i])
                i += 1
            functions[func_name] = (params, body)
            return i + 1  # Skip past the END token
        return None

    elif token[0] == "FUNC_CALL":
        func_name = token[1]
        args = token[2]
        
        if func_name in functions:
            params, body = functions[func_name]
            
            # Create new scope with parameters
            old_scope = current_scope
            new_scope = Scope(old_scope)
            current_scope = new_scope
            
            # Set up parameters in new scope
            for param, arg in zip(params, args):
                value = evaluate_expression(arg, old_scope)
                current_scope.set(param, value)
            
            # Execute function body
            result = None
            for func_token in body:
                result = execute_token(func_token)
                if current_scope.return_value is not None:
                    result = current_scope.return_value
                    break
            
            # Get return value and restore scope
            return_value = current_scope.return_value
            current_scope = old_scope
            return return_value if return_value is not None else result
        else:
            print(f"Function '{func_name}' not defined!")
            return None
    
    elif token[0] == "RETURN":
        if current_scope:
            if token[1]:
                value = evaluate_expression(token[1], current_scope)
                current_scope.return_value = value
            else:
                current_scope.return_value = None
            return current_scope.return_value
        return None

    elif token[0] == "IF":
        if tokens is None or index is None:
            return
        
        condition = evaluate_expression(token[1], current_scope)
        
        i = index + 1
        if condition:
            while i < len(tokens) and tokens[i][0] not in ("ELSE", "END"):
                result = execute_token(tokens[i])
                if current_scope and current_scope.return_value is not None:
                    return result
                i += 1
            while i < len(tokens) and tokens[i][0] != "END":
                i += 1
        else:
            while i < len(tokens) and tokens[i][0] not in ("ELSE", "END"):
                i += 1
            if i < len(tokens) and tokens[i][0] == "ELSE":
                i += 1
                while i < len(tokens) and tokens[i][0] != "END":
                    result = execute_token(tokens[i])
                    if current_scope and current_scope.return_value is not None:
                        return result
                    i += 1
        return i

    elif token[0] == "WHILE":
        if tokens is None or index is None:
            return
        
        i = index + 1
        block_start = i
        while i < len(tokens) and tokens[i][0] != "END":
            i += 1
        block_end = i
        
        while True:
            condition = evaluate_expression(token[1], current_scope)
            if not condition:
                break
                
            j = block_start
            while j < block_end:
                result = execute_token(tokens[j])
                if current_scope and current_scope.return_value is not None:
                    return result
                j += 1
        
        return block_end

    elif token[0] == "FOR":
        if tokens is None or index is None:
            return
        
        var_name, start, end, step = token[1:]
        try:
            start_val = int(evaluate_expression(start, current_scope))
            end_val = int(evaluate_expression(end, current_scope))
            step_val = int(evaluate_expression(step, current_scope))
        except:
            return index + 1
        
        i = index + 1
        block_start = i
        while i < len(tokens) and tokens[i][0] != "END":
            i += 1
        block_end = i
        
        for val in range(start_val, end_val + 1, step_val):
            if current_scope:
                current_scope.set(var_name, val)
            else:
                globals()[var_name] = val
            
            j = block_start
            while j < block_end:
                result = execute_token(tokens[j])
                if current_scope and current_scope.return_value is not None:
                    return result
                j += 1
        
        return block_end

def execute_block(tokens, start_idx, end_condition):
    global loop_context
    i = start_idx
    while i < len(tokens) and not end_condition(tokens[i]):
        if loop_context['break'] or loop_context['continue'] or loop_context['return_value'] is not None:
            break
        execute_token(tokens[i])
        i += 1
    return i

def run(file_path):
    global current_scope
    current_scope = Scope()
    
    with open(file_path, "r") as f:
        code = f.read()

    tokens = tokenize(code)
    i = 0
    while i < len(tokens):
        if tokens[i][0] in ("IF", "WHILE", "FOR", "FUNC_DEF"):
            result = execute_token(tokens[i], tokens, i)
            i = result if result is not None else i + 1
        else:
            execute_token(tokens[i])
            i += 1

if __name__ == "__main__":
    run("examples/function_example.diamond")
