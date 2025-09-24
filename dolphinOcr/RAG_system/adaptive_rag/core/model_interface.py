"""
Generic model interface for different model types
Supports transformer models, RL models, and other architectures
"""

import torch
from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class GenerationConfig:
    """Configuration for text generation"""
    max_new_tokens: int = 512
    temperature: float = 0.7
    do_sample: bool = True
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1

@dataclass
class GenerationResult:
    """Result from text generation"""
    text: str
    tokens_generated: int
    generation_time: float
    model_metadata: Dict[str, Any]

class ModelInterface(ABC):
    """Abstract interface for different model types"""
    
    @abstractmethod
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> GenerationResult:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        pass
    
    @abstractmethod
    def supports_tool_calling(self) -> bool:
        """Check if model supports tool calling"""
        pass

class TransformerModelInterface(ModelInterface):
    """Interface for standard transformer models"""
    
    def __init__(self, model, tokenizer, device=None):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
        
        # Move model to device
        self.model.to(self.device)
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> GenerationResult:
        """Generate text using transformer model"""
        import time
        
        config = config or GenerationConfig()
        start_time = time.time()
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
        
        # Generate
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=config.max_new_tokens,
                temperature=config.temperature,
                do_sample=config.do_sample,
                top_p=config.top_p,
                top_k=config.top_k,
                repetition_penalty=config.repetition_penalty,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode response
        response = self.tokenizer.decode(
            output[0][inputs['input_ids'].shape[1]:], 
            skip_special_tokens=True
        )
        
        generation_time = time.time() - start_time
        tokens_generated = output[0].shape[0] - inputs['input_ids'].shape[1]
        
        return GenerationResult(
            text=response.strip(),
            tokens_generated=tokens_generated,
            generation_time=generation_time,
            model_metadata={
                'model_type': 'transformer',
                'device': str(self.device),
                'config': config.__dict__
            }
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get transformer model information"""
        return {
            'model_type': 'transformer',
            'model_class': type(self.model).__name__,
            'tokenizer_class': type(self.tokenizer).__name__,
            'device': str(self.device),
            'supports_tool_calling': self.supports_tool_calling()
        }
    
    def supports_tool_calling(self) -> bool:
        """Check if transformer model supports tool calling"""
        # This would need to be determined based on the specific model
        # For now, assume it does if it's a chat/instruct model
        return hasattr(self.model, 'generate') and hasattr(self.tokenizer, 'decode')

class RLModelInterface(ModelInterface):
    """Interface for RL fine-tuned models"""
    
    def __init__(self, rl_model, tokenizer=None, device=None):
        self.rl_model = rl_model
        self.tokenizer = tokenizer
        self.device = device or (torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu'))
        
        # Move model to device if it's a torch model
        if hasattr(self.rl_model, 'to'):
            self.rl_model.to(self.device)
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> GenerationResult:
        """Generate text using RL model"""
        import time
        
        config = config or GenerationConfig()
        start_time = time.time()
        
        # This is a placeholder - actual implementation depends on RL model type
        # The RL model might have different interfaces:
        # 1. Standard generate() method
        # 2. Custom inference method
        # 3. Action-based output
        
        if hasattr(self.rl_model, 'generate'):
            # Standard transformer-like interface
            if self.tokenizer:
                inputs = self.tokenizer(prompt, return_tensors='pt').to(self.device)
                with torch.no_grad():
                    output = self.rl_model.generate(
                        **inputs,
                        max_new_tokens=config.max_new_tokens,
                        temperature=config.temperature,
                        do_sample=config.do_sample,
                        pad_token_id=self.tokenizer.eos_token_id if self.tokenizer else None
                    )
                response = self.tokenizer.decode(
                    output[0][inputs['input_ids'].shape[1]:], 
                    skip_special_tokens=True
                )
                tokens_generated = output[0].shape[0] - inputs['input_ids'].shape[1]
            else:
                # Direct text generation
                response = self.rl_model.generate(prompt, **config.__dict__)
                tokens_generated = len(response.split())
        
        elif hasattr(self.rl_model, 'infer'):
            # Custom inference method
            result = self.rl_model.infer(prompt, config.__dict__)
            response = result.get('text', '')
            tokens_generated = result.get('tokens_generated', 0)
        
        else:
            # Fallback - assume it's a callable
            response = self.rl_model(prompt)
            tokens_generated = len(response.split())
        
        generation_time = time.time() - start_time
        
        return GenerationResult(
            text=response.strip(),
            tokens_generated=tokens_generated,
            generation_time=generation_time,
            model_metadata={
                'model_type': 'rl',
                'device': str(self.device),
                'config': config.__dict__
            }
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get RL model information"""
        return {
            'model_type': 'rl',
            'model_class': type(self.rl_model).__name__,
            'device': str(self.device),
            'supports_tool_calling': self.supports_tool_calling()
        }
    
    def supports_tool_calling(self) -> bool:
        """Check if RL model supports tool calling"""
        # This depends on how the RL model was trained
        # Could be determined by checking for specific methods or attributes
        return hasattr(self.rl_model, 'get_tools') or hasattr(self.rl_model, 'tool_calling')

class ModelFactory:
    """Factory for creating model interfaces"""
    
    @staticmethod
    def create_interface(model, tokenizer=None, model_type: str = "auto") -> ModelInterface:
        """Create appropriate model interface"""
        
        if model_type == "auto":
            # Auto-detect model type
            if hasattr(model, 'generate') and tokenizer:
                return TransformerModelInterface(model, tokenizer)
            elif hasattr(model, 'infer') or callable(model):
                return RLModelInterface(model, tokenizer)
            else:
                raise ValueError("Cannot determine model type automatically")
        
        elif model_type == "transformer":
            if not tokenizer:
                raise ValueError("Tokenizer required for transformer model")
            return TransformerModelInterface(model, tokenizer)
        
        elif model_type == "rl":
            return RLModelInterface(model, tokenizer)
        
        else:
            raise ValueError(f"Unknown model type: {model_type}")

# Convenience function for backward compatibility
def create_model_interface(model, tokenizer=None, model_type: str = "auto") -> ModelInterface:
    """Create model interface with backward compatibility"""
    return ModelFactory.create_interface(model, tokenizer, model_type)
