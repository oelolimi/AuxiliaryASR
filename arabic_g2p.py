#!/usr/bin/python
# -*- coding: UTF8 -*-
# Arabic G2P implementation with IPA output for Egyptian Arabic
# Adapted from: https://github.com/nawarhalabi/Arabic-Phonetiser/blob/master/phonetise-Buckwalter.py

import re

class ArabicG2P:
    def __init__(self):
        # Mapping from Arabic script to Buckwalter
        self.arabic_to_buckw_dict = {
            u'\u0628': u'b', u'\u0630': u'*', u'\u0637': u'T', u'\u0645': u'm',
            u'\u062a': u't', u'\u0631': u'r', u'\u0638': u'Z', u'\u0646': u'n',
            u'\u062b': u'^', u'\u0632': u'z', u'\u0639': u'E', u'\u0647': u'h',
            u'\u062c': u'j', u'\u0633': u's', u'\u063a': u'g', u'\u062d': u'H',
            u'\u0642': u'q', u'\u0641': u'f', u'\u062e': u'x', u'\u0635': u'S',
            u'\u0634': u'$', u'\u062f': u'd', u'\u0636': u'D', u'\u0643': u'k',
            u'\u0623': u'>', u'\u0621': u'\'', u'\u0626': u'}', u'\u0624': u'&',
            u'\u0625': u'<', u'\u0622': u'|', u'\u0627': u'A', u'\u0649': u'Y',
            u'\u0629': u'p', u'\u064a': u'y', u'\u0644': u'l', u'\u0648': u'w',
            u'\u064b': u'F', u'\u064c': u'N', u'\u064d': u'K', u'\u064e': u'a',
            u'\u064f': u'u', u'\u0650': u'i', u'\u0651': u'~', u'\u0652': u'o'
        }

        # Buckwalter to IPA mapping for Egyptian Arabic
        self.buckwalter_to_ipa = {
            # Consonants
            'b': 'b', 't': 't', '^': 's',  # ث -> s in Egyptian
            'j': 'g',  # ج -> g in Egyptian (KEY DIFFERENCE)
            'H': 'ħ', 'x': 'x', 'd': 'd', 
            '*': 'z',  # ذ -> z in Egyptian
            'r': 'r', 'z': 'z', 's': 's', 
            '$': 'ʃ',  # ش
            'S': 'sˤ', 'D': 'dˤ', 'T': 'tˤ', 'Z': 'zˤ',  # Emphatics
            'E': 'ʕ',  # ع
            'g': 'ɣ',  # غ
            'f': 'f', 'q': 'q', 'k': 'k', 'l': 'l', 
            'm': 'm', 'n': 'n', 'h': 'h', 'w': 'w', 'y': 'j',
            
            # Hamza variants
            '>': 'ʔ', '<': 'ʔ', '\'': 'ʔ', '}': 'ʔ', '&': 'ʔ',
            '|': 'ʔ',  # Madda
            
            # Ta marboota
            'p': 't',
            
            # Vowels - Short
            'a': 'a', 'i': 'i', 'u': 'u',
            
            # Vowels - Long  
            'aa': 'aː', 'A': 'aː', 'Y': 'aː',  # Different alif forms
            'ii': 'iː', 'uu': 'uː',
            
            # Vowel variants with numbers (from original G2P)
            'i0': 'i', 'i1': 'i',
            'u0': 'u', 'u1': 'u',
            'ii0': 'iː', 'ii1': 'iː',
            'uu0': 'uː', 'uu1': 'uː',
            'I0': 'ɪ', 'I1': 'ɪ',  # Emphatic variants
            'U0': 'ʊ', 'U1': 'ʊ',
            'II0': 'ɪː', 'II1': 'ɪː',
            'UU0': 'ʊː', 'UU1': 'ʊː',
            'AA': 'ɑː',  # Emphatic long a
        }

        # Initialize phoneme mappings (simplified version)
        self.unambiguousConsonantMap = {
            u'b': u'b', u'*': u'*', u'T': u'T', u'm': u'm',
            u't': u't', u'r': u'r', u'Z': u'Z', u'n': u'n',
            u'^': u'^', u'z': u'z', u'E': u'E', u'h': u'h',
            u'j': u'j', u's': u's', u'g': u'g', u'H': u'H',
            u'q': u'q', u'f': u'f', u'x': u'x', u'S': u'S',
            u'$': u'$', u'd': u'd', u'D': u'D', u'k': u'k',
            u'>': u'<', u'\'': u'<', u'}': u'<', u'&': u'<',
            u'<': u'<'
        }

        self.vowelMap = {
            u'A': u'aa', u'Y': u'aa', u'a': u'a',
            u'i': u'i', u'u': u'u'
        }

        self.diacritics = [u'o', u'a', u'u', u'i', u'F', u'N', u'K', u'~']
        self.consonants = [u'>', u'<', u'}', u'&', u'\'', u'b', u't', u'^', u'j', u'H', u'x', u'd', u'*', u'r',
                          u'z', u's', u'$', u'S', u'D', u'T', u'Z', u'E', u'g', u'f', u'q', u'k', u'l', u'm', u'n', u'h', u'|']

    def arabic_to_buckwalter(self, word):
        """Convert input string to Buckwalter"""
        res = ''
        for letter in word:
            if letter in self.arabic_to_buckw_dict:
                res += self.arabic_to_buckw_dict[letter]
            else:
                res += letter
        return res

    def buckwalter_to_ipa_phoneme(self, buckwalter_phoneme):
        """Convert a single Buckwalter phoneme to IPA"""
        # Handle the most common cases first
        if buckwalter_phoneme in self.buckwalter_to_ipa:
            return self.buckwalter_to_ipa[buckwalter_phoneme]
        
        # Handle doubled consonants (gemination)
        if len(buckwalter_phoneme) == 2 and buckwalter_phoneme[0] == buckwalter_phoneme[1]:
            base_phoneme = self.buckwalter_to_ipa.get(buckwalter_phoneme[0], buckwalter_phoneme[0])
            return base_phoneme + base_phoneme  # Gemination
        
        # Fallback for unknown phonemes
        return buckwalter_phoneme

    def preprocess_utterance(self, utterance):
        """Do some normalisation work and split utterance to words"""
        utterance = utterance.replace(u'AF', u'F')
        utterance = utterance.replace(u'\u0640', u'')
        utterance = utterance.replace(u'o', u'')
        utterance = utterance.replace(u'aA', u'A')
        utterance = utterance.replace(u'aY', u'Y')
        utterance = utterance.replace(u' A', u' ')
        utterance = utterance.replace(u'F', u'an')
        utterance = utterance.replace(u'N', u'un')
        utterance = utterance.replace(u'K', u'in')
        utterance = utterance.replace(u'|', u'>A')

        # Deal with Hamza types
        utterance = re.sub(u'Ai', u'<i', utterance)
        utterance = re.sub(u'Aa', u'>a', utterance)
        utterance = re.sub(u'Au', u'>u', utterance)
        utterance = re.sub(u'^>([^auAw])', u'>a\\1', utterance)
        utterance = re.sub(u' >([^auAw ])', u' >a\\1', utterance)
        utterance = re.sub(u'<([^i])', u'<i\\1', utterance)
        utterance = utterance.split(u' ')
        return utterance

    def process_word_simple(self, word):
        """Simplified word processing for better reliability"""
        if not word or word in ['-', 'sil']:
            return ['sil']
        
        # Convert to Buckwalter first
        buckwalter_word = self.arabic_to_buckwalter(word)
        
        # Simple phoneme extraction
        phonemes = []
        i = 0
        while i < len(buckwalter_word):
            char = buckwalter_word[i]
            
            # Check for two-character combinations first
            if i < len(buckwalter_word) - 1:
                two_char = buckwalter_word[i:i+2]
                if two_char in ['aa', 'ii', 'uu', 'AA', 'II', 'UU']:
                    phonemes.append(two_char)
                    i += 2
                    continue
            
            # Single character
            if char in self.unambiguousConsonantMap:
                phonemes.append(self.unambiguousConsonantMap[char])
            elif char in self.vowelMap:
                phonemes.append(self.vowelMap[char])
            elif char in self.consonants or char in ['w', 'y']:
                phonemes.append(char)
            
            i += 1
        
        # Convert Buckwalter phonemes to IPA
        ipa_phonemes = []
        for phoneme in phonemes:
            ipa_phoneme = self.buckwalter_to_ipa_phoneme(phoneme)
            if ipa_phoneme and ipa_phoneme != '':
                ipa_phonemes.append(ipa_phoneme)
        
        return ipa_phonemes if ipa_phonemes else ['sil']

    def process_utterance(self, utterance):
        """Main interface function - converts Arabic text to IPA phonemes"""
        try:
            # Convert Arabic to Buckwalter first
            buckwalter_text = self.arabic_to_buckwalter(utterance)
            
            # Preprocess
            words = self.preprocess_utterance(buckwalter_text)
            
            phonemes = []
            for word in words:
                if word in ['-', 'sil'] or not word.strip():
                    phonemes.append(['sil'])
                    continue
                
                phonemes_word = self.process_word_simple(word)
                phonemes.append(phonemes_word)
            
            # Join phonemes with '+' separator between words and spaces between phonemes within words
            final_sequence = ' + '.join(' '.join(str(phon) for phon in phones) for phones in phonemes)
            return final_sequence
            
        except Exception as e:
            print(f"Error processing utterance '{utterance}': {e}")
            return "sil"

    def __call__(self, text):
        """Make the class callable like the English G2P"""
        return self.process_utterance(text)
