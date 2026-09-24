# coding=utf-8
"""Helper functions untuk training Step 1 dan Step 2.

Modul ini menyediakan fungsi data loading yang compatible dengan
training loop di notebook eksperimen.
"""
import os
import torch
from torch.utils.data import TensorDataset


def load_quad_tsv_dataset(tsv_path, tokenizer, max_seq_length=128):
    """Load dataset dari TSV untuk quad extraction (Step 1).
    
    Format TSV: text####quads	quad1	quad2...
    
    Returns:
        TensorDataset dengan format compatible untuk BertForQuadABSA
    """
    from .taxonomy import ASPECT_LABELS, OPINION_LABELS
    
    instances = []
    with open(tsv_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) < 1:
                continue
            
            # Parse text (sebelum ####)
            text_part = parts[0].split('####')[0]
            tokens = tokenizer.tokenize(text_part)
            
            # Truncate if too long
            if len(tokens) > max_seq_length - 2:
                tokens = tokens[:(max_seq_length - 2)]
            
            # Add [CLS] and [SEP]
            tokens = ['[CLS]'] + tokens + ['[SEP]']
            
            # Convert to IDs
            input_ids = tokenizer.convert_tokens_to_ids(tokens)
            input_mask = [1] * len(input_ids)
            segment_ids = [0] * len(input_ids)
            
            # Pad to max_seq_length
            padding_length = max_seq_length - len(input_ids)
            input_ids += [0] * padding_length
            input_mask += [0] * padding_length
            segment_ids += [0] * padding_length
            
            # Initialize labels (simplified - actual implementation needs quad parsing)
            aspect_labels = [0] * max_seq_length
            opinion_labels = [0] * max_seq_length
            
            # TODO: Parse quads and set proper labels
            # Untuk sekarang gunakan placeholder
            
            instances.append({
                'input_ids': input_ids,
                'input_mask': input_mask,
                'segment_ids': segment_ids,
                'aspect_labels': aspect_labels,
                'opinion_labels': opinion_labels,
            })
    
    # Convert to tensors
    all_input_ids = torch.tensor([inst['input_ids'] for inst in instances], dtype=torch.long)
    all_input_mask = torch.tensor([inst['input_mask'] for inst in instances], dtype=torch.long)
    all_segment_ids = torch.tensor([inst['segment_ids'] for inst in instances], dtype=torch.long)
    all_aspect_labels = torch.tensor([inst['aspect_labels'] for inst in instances], dtype=torch.long)
    all_opinion_labels = torch.tensor([inst['opinion_labels'] for inst in instances], dtype=torch.long)
    
    dataset = TensorDataset(
        all_input_ids,
        all_input_mask,
        all_segment_ids,
        all_aspect_labels,
        all_opinion_labels
    )
    
    return dataset


def compute_extraction_metrics(model, data_loader, device):
    """Hitung precision, recall, F1 untuk extraction task.
    
    Returns:
        dict dengan 'precision', 'recall', 'f1'
    """
    model.eval()
    tp = fp = fn = 0
    
    with torch.no_grad():
        for batch in data_loader:
            batch = tuple(t.to(device) for t in batch)
            input_ids, input_mask, segment_ids, aspect_labels, opinion_labels = batch
            
            # Forward pass
            outputs = model(
                input_ids=input_ids,
                attention_mask=input_mask,
                token_type_ids=segment_ids,
                aspect_labels=aspect_labels,
                opinion_labels=opinion_labels
            )
            
            # Extract predictions
            aspect_preds = outputs.get('aspect_predictions', None)
            opinion_preds = outputs.get('opinion_predictions', None)
            
            if aspect_preds is not None and opinion_preds is not None:
                # Simple token-level evaluation (simplified)
                aspect_preds_flat = aspect_preds.view(-1)
                aspect_labels_flat = aspect_labels.view(-1)
                opinion_preds_flat = opinion_preds.view(-1)
                opinion_labels_flat = opinion_labels.view(-1)
                
                # Count matches (excluding padding)
                mask = (input_mask.view(-1) == 1)
                aspect_correct = ((aspect_preds_flat == aspect_labels_flat) & mask).sum().item()
                opinion_correct = ((opinion_preds_flat == opinion_labels_flat) & mask).sum().item()
                
                # Simplified metrics (seharusnya berbasis span)
                tp += (aspect_correct + opinion_correct)
                fp += 10  # placeholder
                fn += 10  # placeholder
    
    precision = tp / (tp + fp + 1e-9)
    recall = tp / (tp + fn + 1e-9)
    f1 = 2 * precision * recall / (precision + recall + 1e-9)
    
    return {
        'precision': precision,
        'recall': recall,
        'f1': f1 * 100,  # return as percentage
    }


__all__ = [
    'load_quad_tsv_dataset',
    'compute_extraction_metrics',
]

